#!/usr/bin/env python3
"""
WordPress Image Analyzer - simple script to find all <img> tags
"""

import pandas as pd
import json
import re

def load_wp_posts(file_path):
    """Loads posts from JSON export of wp_posts"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # phpMyAdmin export has structure: [header, database, table_with_data]
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get('type') == 'table' and 'data' in item:
                return item['data']  # These are the actual records
    
    # If it's a simple list of records
    if isinstance(data, list):
        return data
        
    return []

def construct_post_url(post, base_url=''):
    """Constructs post URL based on data"""
    post_name = post.get('post_name', '')
    post_type = post.get('post_type', '')
    post_id = post.get('ID', '')
    
    if not post_name:
        return f"{base_url}/?p={post_id}"  # Fallback permalink
    
    # Basic URL structures
    if post_type == 'page':
        return f"{base_url}/{post_name}/"
    elif post_type == 'post':
        return f"{base_url}/{post_name}/"
    else:
        # Custom post types
        return f"{base_url}/{post_type}/{post_name}/"

def find_all_images(posts, base_url=''):
    """Finds all <img> tags in all posts"""
    all_images = []
    debug_stats = {
        'total_posts': 0,
        'filtered_by_status': 0,
        'filtered_by_type': 0,
        'empty_content': 0,
        'processed': 0,
        'with_images': 0
    }
    
    for post in posts:
        debug_stats['total_posts'] += 1
        
        # Only published (publicly visible)
        post_status = post.get('post_status', '')
        if post_status != 'publish':
            debug_stats['filtered_by_status'] += 1
            continue
            
        # Exclude revisions, attachments etc
        post_type = post.get('post_type', '')
        if post_type in ['revision', 'attachment', 'acf-field', 'acf-field-group', 'oembed_cache']:
            debug_stats['filtered_by_type'] += 1
            continue
            
        post_content = post.get('post_content', '')
        if not post_content:
            debug_stats['empty_content'] += 1
            continue
            
        debug_stats['processed'] += 1
        
        # Find all <img> tags
        img_pattern = r'<img[^>]*>'
        matches = list(re.finditer(img_pattern, post_content, re.IGNORECASE))
        
        if matches:
            debug_stats['with_images'] += 1
            print(f"Post {post.get('ID')} ({post_type}): {len(matches)} images - '{post.get('post_title', '')[:50]}'")
        
        for match in matches:
            img_tag = match.group(0)
            
            # Extract src
            src_match = re.search(r'src=["\']([^"\']+)["\']', img_tag, re.IGNORECASE)
            if not src_match:
                continue
                
            # Extract alt
            alt_match = re.search(r'alt=["\']([^"\']*)["\']', img_tag, re.IGNORECASE)
            alt_text = alt_match.group(1) if alt_match else ''
            
            # Context = entire post content (better for LLM)
            clean_content = re.sub(r'<[^>]+>', ' ', post_content)
            clean_content = re.sub(r'\s+', ' ', clean_content).strip()
            
            # Construct post URL
            post_url = construct_post_url(post, base_url)
            
            all_images.append({
                'post_id': post.get('ID'),
                'post_title': post.get('post_title', ''),
                'post_type': post_type,
                'post_status': post_status,
                'post_url': post_url,
                'img_src': src_match.group(1),
                'current_alt': alt_text,
                'has_alt': bool(alt_text.strip()),
                'full_img_tag': img_tag,
                'context': clean_content,  # Entire content as context
                'post_content': post_content  # Raw HTML for backup
            })
    
    print(f"\nDebug statistics:")
    print(f"  Total posts: {debug_stats['total_posts']}")
    print(f"  Filtered by status (!= publish): {debug_stats['filtered_by_status']}")
    print(f"  Filtered by type (revisions, attachments): {debug_stats['filtered_by_type']}")
    print(f"  Empty content: {debug_stats['empty_content']}")
    print(f"  Processed (public content): {debug_stats['processed']}")
    print(f"  With images: {debug_stats['with_images']}")
    
    return all_images

def save_to_excel(images, filename='wordpress_images.xlsx'):
    """Saves to Excel - ready for LLM processing"""
    
    df = pd.DataFrame(images)
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # All images
        df.to_excel(writer, sheet_name='All_Images', index=False)
        
        # Only without alt - for LLM processing
        no_alt = df[df['has_alt'] == False]
        no_alt.to_excel(writer, sheet_name='Needs_Alt_Text', index=False)
        
        # Statistics
        stats = pd.DataFrame({
            'Metric': ['Total images', 'Without alt', 'With alt', '% without alt'],
            'Value': [
                len(df),
                len(no_alt),
                len(df) - len(no_alt),
                f"{round(len(no_alt)/len(df)*100, 1)}%" if len(df) > 0 else "0%"
            ]
        })
        stats.to_excel(writer, sheet_name='Statistics', index=False)
    
    return filename

def main():
    # Configuration
    WORDPRESS_URL = 'https://example.com'  # Change to your WordPress site URL
    export_file = 'wp_posts_export.json'
    output_file = 'wordpress_images.xlsx'
    
    print("Loading data...")
    posts = load_wp_posts(export_file)
    print(f"Loaded {len(posts)} records")
    
    # Debug - show what we have
    if posts:
        print("\nContent types in database:")
        post_types = {}
        statuses = {}
        for post in posts:
            pt = post.get('post_type', 'unknown')
            ps = post.get('post_status', 'unknown')
            post_types[pt] = post_types.get(pt, 0) + 1
            statuses[ps] = statuses.get(ps, 0) + 1
        
        for pt, count in sorted(post_types.items()):
            print(f"  {pt}: {count}")
            
        print(f"\nStatuses:")
        for ps, count in sorted(statuses.items()):
            print(f"  {ps}: {count}")
    
    print("\nSearching for images...")
    images = find_all_images(posts, WORDPRESS_URL)
    print(f"Found {len(images)} images")
    
    if images:
        print("Saving to Excel...")
        save_to_excel(images, output_file)

        no_alt_count = len([img for img in images if not img['has_alt']])
        print(f"\nResults:")
        print(f"Total images: {len(images)}")
        print(f"Without alt: {no_alt_count}")
        print(f"With alt: {len(images) - no_alt_count}")
        print(f"\nSaved: {output_file}")
        print(f"Sheet 'Needs_Alt_Text': {no_alt_count} images ready for processing")
    else:
        print("No images found!")
        print("\nPossible causes:")
        print("- Export contains only ACF fields, not actual posts")
        print("- Posts don't have images in content") 
        print("- All posts are drafts (not published)")
        print("\nCheck if export contains posts of type 'post' or 'page' with status 'publish'")

if __name__ == "__main__":
    main()