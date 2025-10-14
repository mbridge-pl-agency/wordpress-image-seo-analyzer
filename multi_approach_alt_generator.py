#!/usr/bin/env python3
"""
Alt Text Generator - All Approaches
1. Two-step: Vision API → description → Text LLM → alt text
2. One-step (vision): Vision API + context → alt text
3. One-step (text): Only URL + context → alt text
"""

import pandas as pd
from openai import OpenAI
import time
from datetime import datetime

# SET YOUR API KEY
OPENAI_API_KEY = "sk-your-api-key-here"  # CHANGE THIS!

def approach_1_two_step(client, img_url, php_file, context, current_alt, delay=1.0):
    """
    APPROACH 1: Two-step
    Step 1: Vision API - describe image
    Step 2: Text LLM - generate alt based on description + context
    """
    print(f"    [Step 1/2] Analyzing image...")

    # STEP 1: Vision API - image description only
    try:
        description_prompt = "What's in this image? Describe what you see in detail. Focus on the main elements, colors, text, people, objects, and overall composition."

        description_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": description_prompt},
                    {"type": "image_url", "image_url": {"url": img_url}}
                ]
            }]
        )

        image_description = description_response.choices[0].message.content.strip()
        print(f"    Description: {image_description[:100]}...")
        
        time.sleep(delay)
        
    except Exception as e:
        return {"success": False, "error": f"Step 1 error: {str(e)}", "image_description": "", "alt_text": ""}
    
    print(f"    [Step 2/2] Generating alt text...")
    
    # STEP 2: Text LLM - alt text based on description + context
    try:
        alt_prompt = f"""You are creating an alt text for an image in a WordPress PHP template file.

IMAGE URL: {img_url}
PHP TEMPLATE FILE: {php_file}
CURRENT ALT TEXT: "{current_alt}" (empty if none)

DETAILED IMAGE DESCRIPTION:
{image_description}

CODE CONTEXT around the image tag:
```php
{context}
```

INSTRUCTIONS:
- Use the detailed image description and code context to create the perfect alt text
- This image is part of a website template (header, footer, layout elements)
- Consider if it's a logo, icon, decorative element, or content image
- **If the image shows a person, try to identify them from the page context (text, names mentioned)**
- **For people: include their name and title/role if mentioned in the context**

REQUIREMENTS:
- Maximum 125 characters
- Be descriptive and helpful for accessibility
- Don't use words like "image", "picture", "photo"
- For logos: include company/organization name
- For icons: describe the function/meaning
- For people: include name and title if identifiable from context
- For decorative elements: consider if alt should be empty
- Be specific and contextual

EXAMPLE: If you see a person and context mentions "Dr. Jane Smith, Professor of Medicine" 
→ Alt text: "Dr. Jane Smith, Professor of Medicine, in professional portrait"

RESPONSE: Provide only the alt text, nothing else. If the image is purely decorative, respond with "DECORATIVE"."""

        alt_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": alt_prompt}],
            temperature=0.3
        )
        
        alt_text = alt_response.choices[0].message.content.strip().strip('"\'')
        
        # Handle decorative images
        if alt_text == "DECORATIVE":
            alt_text = ""
            status = "decorative"
        else:
            status = "success"
        
        return {
            "success": True, 
            "image_description": image_description, 
            "alt_text": alt_text,
            "status": status
        }
        
    except Exception as e:
        return {
            "success": False, 
            "error": f"Step 2 error: {str(e)}", 
            "image_description": image_description, 
            "alt_text": ""
        }

def approach_2_one_step_vision(client, img_url, php_file, context, current_alt):
    """
    APPROACH 2: One-step with Vision API
    Vision API + context → alt text in one step
    """
    print(f"    Analyzing with vision API...")
    
    try:
        prompt = f"""You are creating an alt text for an image found in a WordPress PHP template file.

IMAGE URL: {img_url}
PHP TEMPLATE FILE: {php_file}
CURRENT ALT TEXT: "{current_alt}" (empty if none)

CODE CONTEXT around the image tag:
```php
{context}
```

INSTRUCTIONS:
- Look at the image and understand what it shows
- This image is part of the website template (header, footer, layout elements)
- Consider if it's a logo, icon, decorative element, or content image
- The context shows where in the PHP template this image appears
- **If the image shows a person, try to identify them from the page context (text, names mentioned)**
- **For people: include their name and title/role if mentioned in the context**

REQUIREMENTS:
- Maximum 125 characters
- Be descriptive and helpful for accessibility
- Don't use words like "image", "picture", "photo"
- For logos: include company/organization name
- For icons: describe the function/meaning
- For people: include name and title if identifiable from context
- For decorative elements: consider if alt should be empty
- Be specific and contextual

EXAMPLE: If you see a person and context mentions "Dr. Jane Smith, Professor of Medicine" 
→ Alt text: "Dr. Jane Smith, Professor of Medicine, in professional portrait"

RESPONSE: Provide only the alt text, nothing else. If the image is purely decorative, respond with "DECORATIVE"."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": img_url}}
                ]
            }],
            temperature=0.3
        )
        
        alt_text = response.choices[0].message.content.strip().strip('"\'')
        
        if alt_text == "DECORATIVE":
            alt_text = ""
            status = "decorative"
        else:
            status = "success"
        
        return {
            "success": True, 
            "image_description": "Generated with vision in one step", 
            "alt_text": alt_text,
            "status": status
        }
        
    except Exception as e:
        return {"success": False, "error": str(e), "image_description": "", "alt_text": ""}

def approach_3_text_only(client, img_url, php_file, context, current_alt):
    """
    APPROACH 3: Text only
    Only URL + context → alt text (no image analysis)
    """
    print(f"    Generating from context (text-only)...")
    
    try:
        prompt = f"""You are creating an alt text for an image found in a WordPress PHP template file.

IMAGE URL: {img_url}
PHP TEMPLATE FILE: {php_file}
CURRENT ALT TEXT: "{current_alt}" (empty if none)

CODE CONTEXT around the image tag:
```php
{context}
```

INSTRUCTIONS:
- Based on the image URL and context, create an appropriate alt text
- This image is part of the website template (header, footer, layout elements)
- Consider if it's a logo, icon, decorative element, or content image
- Look at the filename and path for clues about the image content
- The context shows where in the PHP template this image appears
- **If the context suggests the image shows a person, try to identify them from the text**
- **For people: include their name and title/role if mentioned in the context**

REQUIREMENTS:
- Maximum 125 characters
- Be descriptive and helpful for accessibility
- Don't use words like "image", "picture", "photo"
- For logos: include company/organization name
- For icons: describe the function/meaning
- For people: include name and title if identifiable from context
- For decorative elements: consider if alt should be empty
- Be specific and contextual based on filename and context

EXAMPLE: If filename is "dr-smith-portrait.jpg" and context mentions "Dr. Jane Smith, Professor" 
→ Alt text: "Dr. Jane Smith, Professor of Medicine, in professional portrait"

RESPONSE: Provide only the alt text, nothing else. If the image is purely decorative, respond with "DECORATIVE"."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        alt_text = response.choices[0].message.content.strip().strip('"\'')
        
        if alt_text == "DECORATIVE":
            alt_text = ""
            status = "decorative"
        else:
            status = "success"
        
        return {
            "success": True, 
            "image_description": "Generated from filename/context only", 
            "alt_text": alt_text,
            "status": status
        }
        
    except Exception as e:
        return {"success": False, "error": str(e), "image_description": "", "alt_text": ""}

def generate_alt_texts_multi_approach(df, client, approach, delay=1.0):
    """
    Generates alt texts using the selected approach
    """
    approach_names = {
        1: "Two-step (Vision + Text)",
        2: "One-step (Vision)",
        3: "One-step (Text)"
    }
    
    print(f"Generating alt texts - {approach_names[approach]}...")
    
    # Add columns if they don't exist
    if 'ai_image_description' not in df.columns:
        df['ai_image_description'] = ''
    if 'ai_alt_text' not in df.columns:
        df['ai_alt_text'] = ''
    if 'ai_analysis_status' not in df.columns:
        df['ai_analysis_status'] = ''
    if 'ai_approach_used' not in df.columns:
        df['ai_approach_used'] = ''
    
    total = len(df)
    processed = 0
    successful = 0
    
    for index, row in df.iterrows():
        # Skip if already has alt text
        current_ai_alt = row.get('ai_alt_text', '')
        if current_ai_alt and str(current_ai_alt).strip() and not str(current_ai_alt).startswith('ERROR'):
            print(f"[{index+1}/{total}] Already has alt text, skipping")
            continue
            
        try:
            processed += 1
            
            img_url = row['src_absolute_url']
            php_file = row['php_file']
            context = row.get('line_context', '')
            current_alt = row.get('current_alt', '')
            
            print(f"[{processed}/{total}] {img_url}")
            print(f"    From file: {php_file}")
            
            # Select approach
            if approach == 1:
                result = approach_1_two_step(client, img_url, php_file, context, current_alt, delay)
            elif approach == 2:
                result = approach_2_one_step_vision(client, img_url, php_file, context, current_alt)
            else:  # approach == 3
                result = approach_3_text_only(client, img_url, php_file, context, current_alt)
            
            # Save results
            if result["success"]:
                df.at[index, 'ai_image_description'] = result["image_description"]
                df.at[index, 'ai_alt_text'] = result["alt_text"]
                df.at[index, 'ai_analysis_status'] = result["status"]
                df.at[index, 'ai_approach_used'] = approach_names[approach]
                successful += 1
                
                print(f"    Alt text: '{result['alt_text']}'")
                if result["alt_text"] == "":
                    print(f"    (marked as decorative)")
            else:
                df.at[index, 'ai_alt_text'] = f"ERROR: {result['error']}"
                df.at[index, 'ai_analysis_status'] = 'error'
                df.at[index, 'ai_approach_used'] = approach_names[approach]
                print(f"    ERROR: {result['error']}")
            
            # Delay between requests (for approach 1, delay is in the function)
            if approach != 1:
                time.sleep(delay)
            
        except Exception as e:
            print(f"ERROR: General error for {img_url}: {e}")
            df.at[index, 'ai_alt_text'] = f"ERROR: {str(e)}"
            df.at[index, 'ai_analysis_status'] = 'error'
            continue

    print(f"\nCompleted! Processed {processed} images, successful: {successful}")
    return df

def main():
    """Main function"""

    print("ALT TEXT GENERATOR - ALL APPROACHES")
    print("=" * 60)

    if OPENAI_API_KEY == "sk-your-api-key-here":
        print("ERROR: Set your OpenAI API key in the OPENAI_API_KEY variable")
        return
    
    # Get Excel file path
    excel_file = input("Enter path to Excel file: ").strip().strip('"')
    
    if not excel_file.endswith('.xlsx'):
        excel_file += '.xlsx'
    
    try:
        # Check available sheets
        excel_sheets = pd.ExcelFile(excel_file).sheet_names
        print(f"\nAvailable sheets: {', '.join(excel_sheets)}")

        # Select sheet
        if len(excel_sheets) == 1:
            sheet_name = excel_sheets[0]
            print(f"Using the only sheet: {sheet_name}")
        else:
            sheet_name = input(f"Choose sheet (default '{excel_sheets[0]}'): ").strip()
            if not sheet_name:
                sheet_name = excel_sheets[0]
        
        # Load data
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        print(f"Loaded {len(df)} rows from sheet '{sheet_name}'")
        
    except FileNotFoundError:
        print(f"ERROR: File not found: {excel_file}")
        return
    except Exception as e:
        print(f"ERROR: Loading error: {e}")
        return
    
    # Check required columns
    required_columns = ['src_absolute_url', 'php_file']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"ERROR: Missing required columns: {missing_columns}")
        print(f"Available columns: {list(df.columns)}")
        return
    
    # Show statistics
    total_images = len(df)
    
    if 'ai_alt_text' in df.columns:
        with_ai_alt = len(df[df['ai_alt_text'].notna() & 
                            (df['ai_alt_text'].astype(str).str.strip() != '') &
                            ~df['ai_alt_text'].astype(str).str.startswith('ERROR')])
    else:
        with_ai_alt = 0
    
    without_ai_alt = total_images - with_ai_alt

    print(f"\nSTATISTICS:")
    print(f"   Total images: {total_images}")
    print(f"   With AI alt text: {with_ai_alt}")
    print(f"   Without AI alt text: {without_ai_alt}")

    # Select approach
    print(f"\nCHOOSE APPROACH:")
    print("1. Two-step: Vision API (description) → Text LLM (alt text)")
    print("   Most accurate, but most expensive and slowest")
    print("2. One-step (vision): Vision API + context → alt text")
    print("   Faster than two-step, good quality")
    print("3. One-step (text): Only URL + context → alt text")
    print("   Fastest and cheapest, based on filenames")
    
    while True:
        approach_choice = input("\nChoose approach (1/2/3): ").strip()
        if approach_choice in ['1', '2', '3']:
            approach = int(approach_choice)
            break
        print("ERROR: Invalid choice, enter 1, 2 or 3")

    approach_names = {
        1: "Two-step (Vision + Text)",
        2: "One-step (Vision)",
        3: "One-step (Text)"
    }
    print(f"Selected: {approach_names[approach]}")

    # Filtering options
    print(f"\nWHICH IMAGES TO PROCESS:")
    print("1. All images (overwrite existing AI alt texts)")
    print("2. Only images without AI alt text")
    print("3. Test on first 3 images")
    print("4. Specific row range")
    
    filter_choice = input("Choose option (1/2/3/4): ").strip()
    
    # Prepare data for processing
    if filter_choice == "1":
        df_to_process = df.copy()
        # Clear existing AI data
        df_to_process['ai_alt_text'] = ''
        df_to_process['ai_analysis_status'] = ''
        if 'ai_image_description' in df_to_process.columns:
            df_to_process['ai_image_description'] = ''
        print(f"Processing all {len(df)} images (overwriting)")
        
    elif filter_choice == "2":
        if 'ai_alt_text' in df.columns:
            mask = df['ai_alt_text'].isna() | \
                   (df['ai_alt_text'].astype(str).str.strip() == '') | \
                   df['ai_alt_text'].astype(str).str.startswith('ERROR')
            df_to_process = df[mask].copy()
        else:
            df_to_process = df.copy()
        print(f"Processing {len(df_to_process)} images without AI alt text")
        
    elif filter_choice == "3":
        df_to_process = df.head(3).copy()
        print("Test mode - first 3 images")
        
    elif filter_choice == "4":
        try:
            start = int(input("From which row? (1-based): ")) - 1
            end = int(input("To which row? (1-based): "))
            df_to_process = df.iloc[start:end].copy()
            print(f"Processing rows {start+1}-{end}")
        except ValueError:
            print("ERROR: Invalid range, using test mode")
            df_to_process = df.head(3).copy()
    else:
        print("ERROR: Invalid choice, using option 2")
        if 'ai_alt_text' in df.columns:
            mask = df['ai_alt_text'].isna() | \
                   (df['ai_alt_text'].astype(str).str.strip() == '')
            df_to_process = df[mask].copy()
        else:
            df_to_process = df.copy()

    if len(df_to_process) == 0:
        print("ERROR: No images to process")
        return

    print(f"\nTo process: {len(df_to_process)} images")
    
    # Set delay
    if approach == 1:
        delay = float(input("Delay between steps (seconds, default 1.0): ") or "1.0")
        print("Note: Two-step approach makes 2 requests per image")
    else:
        delay = float(input("Delay between requests (seconds, default 1.0): ") or "1.0")

    # Estimated costs
    estimated_requests = len(df_to_process) * (2 if approach == 1 else 1)
    print(f"\nESTIMATED COSTS:")
    if approach == 1:
        print(f"   Requests: {estimated_requests} (Vision: {len(df_to_process)}, Text: {len(df_to_process)})")
        print(f"   Cost: ~${estimated_requests * 0.01:.2f}")
    elif approach == 2:
        print(f"   Requests: {estimated_requests} (Vision)")
        print(f"   Cost: ~${estimated_requests * 0.01:.2f}")
    else:
        print(f"   Requests: {estimated_requests} (Text)")
        print(f"   Cost: ~${estimated_requests * 0.005:.2f}")
    
    # Confirm
    confirm = input(f"\nAre you sure you want to continue? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Cancelled")
        return
    
    # Initialize OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # Generate alt texts
    start_time = time.time()
    try:
        df_to_process = generate_alt_texts_multi_approach(df_to_process, client, approach, delay)
        
        # Update main DataFrame
        for idx in df_to_process.index:
            if idx in df.index:
                df.at[idx, 'ai_alt_text'] = df_to_process.at[idx, 'ai_alt_text']
                df.at[idx, 'ai_analysis_status'] = df_to_process.at[idx, 'ai_analysis_status']
                df.at[idx, 'ai_approach_used'] = df_to_process.at[idx, 'ai_approach_used']
                if 'ai_image_description' in df_to_process.columns:
                    df.at[idx, 'ai_image_description'] = df_to_process.at[idx, 'ai_image_description']

    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"php_images_approach_{approach}_{timestamp}.xlsx"
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Save updated data
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Additional sheets
        if 'ai_analysis_status' in df.columns:
            successful_alts = df[df['ai_analysis_status'] == 'success']
            if not successful_alts.empty:
                successful_alts.to_excel(writer, sheet_name='Success', index=False)
            
            decorative_alts = df[df['ai_analysis_status'] == 'decorative']
            if not decorative_alts.empty:
                decorative_alts.to_excel(writer, sheet_name='Decorative', index=False)
            
            error_alts = df[df['ai_analysis_status'] == 'error']
            if not error_alts.empty:
                error_alts.to_excel(writer, sheet_name='Errors', index=False)
        
        # Statistics
        total_count = len(df)
        success_count = len(df[df['ai_analysis_status'] == 'success']) if 'ai_analysis_status' in df.columns else 0
        decorative_count = len(df[df['ai_analysis_status'] == 'decorative']) if 'ai_analysis_status' in df.columns else 0
        error_count = len(df[df['ai_analysis_status'] == 'error']) if 'ai_analysis_status' in df.columns else 0
        
        stats_data = {
            'Metric': [
                'Approach used',
                'Processing time (seconds)',
                'Total number of images',
                'Generated alt texts (success)',
                'Marked as decorative',
                'Generation errors',
                'Total AI alt texts'
            ],
            'Value': [
                approach_names[approach],
                f"{duration:.1f}",
                total_count,
                success_count,
                decorative_count,
                error_count,
                success_count + decorative_count
            ]
        }
        stats_df = pd.DataFrame(stats_data)
        stats_df.to_excel(writer, sheet_name='Statistics', index=False)

    print(f"\nDONE! Results saved in: {output_file}")
    print(f"Processing time: {duration/60:.1f} minutes")

    # Show final statistics
    if 'ai_analysis_status' in df.columns:
        successful_count = len(df[df['ai_analysis_status'] == 'success'])
        decorative_count = len(df[df['ai_analysis_status'] == 'decorative'])
        error_count = len(df[df['ai_analysis_status'] == 'error'])
    else:
        successful_count = 0
        decorative_count = 0
        error_count = 0

    print(f"\nRESULTS - {approach_names[approach]}:")
    print(f"   Generated alt texts: {successful_count}")
    print(f"   Marked as decorative: {decorative_count}")
    print(f"   Errors: {error_count}")

    # Show examples
    if successful_count > 0:
        successful_df = df[df['ai_analysis_status'] == 'success']
        print(f"\nEXAMPLES OF GENERATED ALT TEXTS:")
        for i, (_, row) in enumerate(successful_df.head(3).iterrows()):
            print(f"{i+1}. {row['php_file']}")
            print(f"   URL: {row['src_absolute_url']}")
            print(f"   Alt: '{row['ai_alt_text']}'")
            if approach == 1 and 'ai_image_description' in row:
                desc = row['ai_image_description']
                if desc and len(desc) > 5:
                    print(f"   Description: {desc[:80]}...")
            print()

if __name__ == "__main__":
    main()