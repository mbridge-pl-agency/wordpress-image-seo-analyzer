# WordPress Image SEO & Accessibility Analyzer

Automated tools for analyzing and generating alt texts for images in WordPress websites using OpenAI's Vision API. Improve both **SEO rankings** and **web accessibility** compliance.

## Overview

Alt text attributes serve two critical purposes:
1. **SEO Optimization** - Search engines use alt text to understand and index images, improving search rankings
2. **Web Accessibility** - Screen readers rely on alt text to describe images to visually impaired users

This project provides two Python scripts to audit and optimize image alt texts across WordPress sites:

1. **WordPress Image Analyzer** - Extracts all images from WordPress database and identifies missing alt texts
2. **Multi-Approach Alt Generator** - Automatically generates SEO-friendly and accessible alt texts using OpenAI's GPT-4 Vision API

## Key Features

### WordPress Image Analyzer
- Exports image data from WordPress `wp_posts` table
- Identifies images missing alt text attributes
- Generates Excel reports with:
  - All images found in published content
  - Images requiring alt text
  - Statistics and metrics
- Constructs direct URLs to pages containing images for easy verification

### Multi-Approach Alt Generator
- **Three generation strategies:**
  1. **Two-step**: Vision API describes image, then Text LLM generates optimized alt text (most accurate)
  2. **One-step (vision)**: Vision API with context generates alt text directly (balanced approach)
  3. **One-step (text)**: Context and filename only, no image analysis (fastest and most cost-effective)
- Context-aware generation using surrounding page content
- Identifies decorative images that should have empty alt text
- Batch processing with progress tracking
- Cost estimation before processing
- Detailed Excel reports with results

## Requirements

- Python 3.7+
- OpenAI API key (for alt text generation)
- Access to WordPress database

## Installation

1. Clone this repository:
```bash
git clone https://github.com/mbridge-pl-agency/wordpress-image-seo-analyzer.git
cd wordpress-image-seo-analyzer
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key in `multi_approach_alt_generator.py`:
```python
OPENAI_API_KEY = "sk-your-api-key-here"
```

## Usage

### Step 1: Extract Images from WordPress

1. Export the `wp_posts` table from your WordPress database:
   - Open phpMyAdmin
   - Select your WordPress database
   - Navigate to the `wp_posts` table
   - Click **Export** → Format: **JSON**
   - Save as `wp_posts_export.json`

2. Update the WordPress URL in `wordpress_image_analyzer.py`:
```python
WORDPRESS_URL = 'https://example.com'  # Change to your site URL
```

3. Run the analyzer:
```bash
python wordpress_image_analyzer.py
```

4. Output: `wordpress_images.xlsx` with sheets:
   - **All_Images** - Complete list of images
   - **Needs_Alt_Text** - Images missing alt text
   - **Statistics** - Summary metrics

### Step 2: Generate Alt Texts with AI

1. Run the generator:
```bash
python multi_approach_alt_generator.py
```

2. Follow the interactive prompts:
   - Select the Excel file to process
   - Choose generation approach (1/2/3)
   - Select which images to process
   - Review cost estimate and confirm

3. Output: New Excel file with generated alt texts:
   - **Success** - Images with generated alt text
   - **Decorative** - Images marked as decorative
   - **Errors** - Processing errors
   - **Statistics** - Generation metrics

## Generation Approaches

| Approach | Description | Speed | Cost | Accuracy | Best For |
|----------|-------------|-------|------|----------|----------|
| **1. Two-step** | Vision API → description<br>Text LLM → alt text | Slowest | Highest | Best | Important content images, people portraits, complex scenes |
| **2. One-step (vision)** | Vision API + context → alt text | Medium | Medium | Good | General use, balanced quality and cost |
| **3. One-step (text)** | Filename + context → alt text | Fastest | Lowest | Basic | Large batches, images with descriptive filenames |

### Approach Selection Guide
- **Approach 1**: Use for hero images, product photos, team member portraits, or any image central to page content
- **Approach 2**: Recommended for most use cases - good balance of quality, speed, and cost
- **Approach 3**: Best for bulk processing when images have descriptive filenames (e.g., `blue-widget-product.jpg`)

## Example Output

```
Loaded 1,245 records
Found 67 images

Results:
Total images: 67
Without alt: 62 (92.5%)
With alt: 5 (7.5%)

Saved: wordpress_images.xlsx
Sheet 'Needs_Alt_Text': 62 images ready for processing
```

## SEO Benefits

Proper alt text implementation provides:
- **Improved image search rankings** - Google Images and other search engines can index your content
- **Better overall page SEO** - Alt text contributes to page relevance signals
- **Enhanced user experience** - Users on slow connections see descriptive text while images load
- **Increased traffic** - Images appearing in search results drive additional organic traffic

## Cost Estimation

Approximate costs for OpenAI API usage:
- **Approach 1**: ~$0.01 per image (2 API calls)
- **Approach 2**: ~$0.01 per image (1 Vision API call)
- **Approach 3**: ~$0.005 per image (1 Text API call)

Example: Processing 100 images with Approach 2 costs approximately $1.00

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is designed to assist with SEO optimization and web accessibility compliance. Always review generated alt texts before deploying to production to ensure accuracy, brand consistency, and appropriateness.

## Related Resources

- [WCAG 2.1 Guidelines for Images](https://www.w3.org/WAI/WCAG21/Understanding/non-text-content.html)
- [Google Image SEO Best Practices](https://developers.google.com/search/docs/advanced/guidelines/google-images)
- [OpenAI Vision API Documentation](https://platform.openai.com/docs/guides/vision)
- [WordPress Accessibility Handbook](https://make.wordpress.org/accessibility/handbook/)

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Keywords**: WordPress SEO, image optimization, alt text generator, web accessibility, WCAG compliance, OpenAI Vision API, automated SEO tools
