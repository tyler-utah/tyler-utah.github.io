# Tyler Sorensen - Academic Website

A clean, minimal academic website built with plain HTML and CSS. No frameworks, no build steps, no dependencies that break.

## 🚀 Quick Start with GitHub Pages

1. **Create a new repository** on GitHub named `your-username.github.io`
2. **Upload these files** to the repository:
   - `index.html`
   - `style.css`
   - `photo.jpg` (add your photo)
   - `cv.pdf` (add your CV)
3. **Enable GitHub Pages**: Go to Settings → Pages → Source: "Deploy from a branch" → Branch: `main`
4. Your site will be live at `https://your-username.github.io`

## ✏️ How to Update (from GitHub Web Interface)

You can edit everything directly from GitHub.com:

1. Go to your repository
2. Click on `index.html`
3. Click the pencil icon (Edit this file)
4. Make your changes
5. Click "Commit changes"
6. Your site updates automatically in ~1 minute!

## 📝 What to Update Where

### Adding News Items
Find the `<!-- NEWS -->` section and add a new `<li>` item:
```html
<li><strong>2024:</strong> Your news here</li>
```

### Adding a Publication
Copy an existing `<div class="pub">` block and modify:
```html
<div class="pub">
    <span class="pub-title">Paper Title</span>
    <span class="pub-authors">Author 1, Author 2, Author 3</span>
    <span class="pub-venue">CONFERENCE, YEAR</span>
    <span class="pub-links">
        <a href="paper.pdf">[PDF]</a>
    </span>
</div>
```

For award-winning papers, add:
```html
<span class="pub-award">🏆 Best Paper Award</span>
```

### Adding/Removing Students
Find the Students section and edit the `<ul>` lists:
```html
<li><a href="https://student-website.com">Student Name</a> - Started Fall 2024</li>
```

### Adding a Project
```html
<div class="project">
    <h3><a href="https://project-url.com">Project Name</a></h3>
    <p>Brief description of the project.</p>
</div>
```

### Adding a Course
```html
<li><strong>CSE XXX:</strong> Course Name - 
    <a href="course-url">Semester Year</a></li>
```

## 🎨 Customizing Colors

Edit the `:root` section at the top of `style.css`:

```css
:root {
    --primary-color: #1a365d;    /* Headers, links */
    --accent-color: #2b6cb0;     /* Hover states, highlights */
    --text-color: #2d3748;       /* Body text */
    --light-text: #718096;       /* Secondary text */
}
```

## 📁 Files

| File | Purpose |
|------|---------|
| `index.html` | All your content |
| `style.css` | All styling |
| `photo.jpg` | Your profile photo |
| `cv.pdf` | Your CV (linked from header) |

## ✅ TODO Before Publishing

- [ ] Add your photo as `photo.jpg` (recommended: 400x400px or larger, square)
- [ ] Add your CV as `cv.pdf`
- [ ] Update Google Scholar link (search for your Google Scholar profile and copy the URL)
- [ ] Update GitHub link if needed
- [ ] Update email address
- [ ] Review all sections for accuracy

## 🔗 Useful Links

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Custom Domain Setup](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)

## Why Plain HTML?

- **Zero maintenance**: No npm, no build steps, no updates
- **Guaranteed to work**: HTML/CSS hasn't had breaking changes in decades
- **Fast**: No JavaScript, no frameworks, instant load
- **Editable anywhere**: GitHub web interface, any text editor
- **Forever compatible**: This site will work in 10 years without changes
