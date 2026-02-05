# Integrity Debt Audit: 100 Persona Beta Test

## Tool Capabilities Tested
- **File Upload:** PDF, DOCX
- **Text Paste:** Direct text input
- **URL Scrape:** Public web pages

---

## CATEGORY A: Users with Own Assessments (40 personas)

### A1: PDF Users (15 personas)

| # | Persona | Scenario | Likely Outcome | Potential Issue |
|---|---------|----------|----------------|-----------------|
| 1 | Lecturer with polished PDF | Uploads well-formatted module handbook | ✅ Works | None |
| 2 | Admin with scanned PDF | Uploads scanned/image-based PDF | ❌ Fails | **No OCR support** - tool cannot read image-based PDFs |
| 3 | Lecturer with PDF from VLE | Downloads from Moodle, uploads | ✅ Works | None |
| 4 | Part-time tutor on phone | Tries to upload from mobile | ⚠️ Friction | Mobile file picker is clunky |
| 5 | Academic with password-protected PDF | Uploads encrypted PDF | ❌ Fails | **No encrypted PDF support** |
| 6 | Course leader with 50-page handbook | Uploads very long document | ⚠️ Slow | May hit API token limits or timeout |
| 7 | Lecturer with non-English PDF | Uploads Spanish assessment | ⚠️ Partial | Tool may work but not tested for non-English |
| 8 | New lecturer with minimal brief | Uploads 1-paragraph assessment | ⚠️ Poor results | Brief too short for meaningful analysis |
| 9 | Professor with complex tables | PDF has marking rubric tables | ⚠️ Partial | Table extraction may be lossy |
| 10 | TA with merged PDF | Multiple assessments in one file | ⚠️ Confusing | Tool analyses as single document |
| 11 | Lecturer with PDF from Google Docs | Exports as PDF, uploads | ✅ Works | None |
| 12 | Academic with corrupted PDF | Damaged file | ❌ Fails | Error handling exists but may confuse user |
| 13 | Lecturer with emoji in filename | "Assessment Brief 📚.pdf" | ⚠️ Maybe | Special characters in filename |
| 14 | Module lead with PDF/A format | Archival PDF format | ✅ Works | pypdf handles PDF/A |
| 15 | Academic with form-fillable PDF | Interactive PDF with fields | ⚠️ Partial | May not extract form field content |

### A2: Word Document Users (15 personas)

| # | Persona | Scenario | Likely Outcome | Potential Issue |
|---|---------|----------|----------------|-----------------|
| 16 | Lecturer with .docx | Standard Word document | ✅ Works | None |
| 17 | Lecturer with .doc | Older Word format | ❌ Fails | **Only .docx supported, not .doc** |
| 18 | Academic with tracked changes | Document with revisions visible | ⚠️ Messy | May extract revision marks as text |
| 19 | Lecturer with comments | Document with margin comments | ⚠️ Messy | Comments may be extracted or ignored |
| 20 | Course team with shared template | Standard uni template | ✅ Works | None |
| 21 | Academic with embedded images | Brief includes diagrams | ⚠️ Partial | Images ignored, only text extracted |
| 22 | Lecturer with headers/footers | Uni branding in header | ✅ Works | Header text extracted (may add noise) |
| 23 | Part-timer with Google Doc | Wants to upload Google Doc directly | ❌ Fails | **Must export to .docx first** |
| 24 | TA with LibreOffice .odt | Uses open source software | ❌ Fails | **Only .docx supported, not .odt** |
| 25 | Lecturer with .docm | Macro-enabled Word doc | ❌ Fails | **Only .docx supported** |
| 26 | Academic with large tables | Complex rubric in Word table | ⚠️ Partial | Table extraction may lose structure |
| 27 | Module lead with text boxes | Design elements in Word | ⚠️ Partial | Text boxes may not extract properly |
| 28 | Lecturer with footnotes | Academic-style with references | ✅ Works | Footnotes extracted |
| 29 | Academic with hyperlinks | Links to VLE resources | ✅ Works | Link text extracted, URLs may be lost |
| 30 | Course leader with master doc | Uses Word master document feature | ⚠️ Partial | May only get main doc content |

### A3: Text Paste Users (10 personas)

| # | Persona | Scenario | Likely Outcome | Potential Issue |
|---|---------|----------|----------------|-----------------|
| 31 | Lecturer copying from VLE | Copies text from Moodle | ✅ Works | Formatting lost but content preserved |
| 32 | Academic copying from email | Pastes brief from colleague's email | ✅ Works | None |
| 33 | Course leader drafting | Writes brief directly in text box | ✅ Works | None |
| 34 | Lecturer copying from PDF | Ctrl+C from PDF, paste | ⚠️ Partial | PDF copy often has line break issues |
| 35 | Academic with rich text | Copies formatted text | ✅ Works | Formatting stripped, content preserved |
| 36 | TA with very short text | Pastes just the assignment question | ⚠️ Poor results | Too little context for good analysis |
| 37 | Lecturer with bullet points | Copies bulleted list | ✅ Works | Bullets become plain text |
| 38 | Academic copying from Word | Ctrl+C from Word | ✅ Works | Clean text extraction |
| 39 | Module lead with markdown | Pastes markdown-formatted text | ✅ Works | Markdown rendered as plain text |
| 40 | Professor with HTML tags | Accidentally includes HTML | ✅ Works | Tags treated as text (may add noise) |

---

## CATEGORY B: URL/HTML Users (25 personas)

| # | Persona | Scenario | Likely Outcome | Potential Issue |
|---|---------|----------|----------------|-----------------|
| 41 | Lecturer with public course page | Pastes public uni URL | ✅ Works | BeautifulSoup extracts text |
| 42 | Academic with Moodle link | Pastes Moodle URL (authenticated) | ❌ Fails | **Cannot access login-protected pages** |
| 43 | Course leader with Canvas link | Pastes Canvas URL | ❌ Fails | **Cannot access login-protected pages** |
| 44 | Lecturer with Blackboard link | Pastes Blackboard URL | ❌ Fails | **Cannot access login-protected pages** |
| 45 | TA with Google Doc link | Pastes Google Doc sharing link | ⚠️ Partial | May work if truly public, often fails |
| 46 | Academic with OneDrive link | Pastes OneDrive sharing URL | ⚠️ Partial | Often requires sign-in |
| 47 | Professor with Dropbox link | Pastes Dropbox link | ⚠️ Partial | May redirect, extraction unreliable |
| 48 | Lecturer with JavaScript-heavy site | Modern SPA course page | ❌ Fails | **BeautifulSoup doesn't execute JS** |
| 49 | Academic with PDF URL | Direct link to PDF file | ❌ Fails | **URL scraper expects HTML, not PDF** |
| 50 | Course team with blog post | Public blog with assessment info | ✅ Works | Extracts article text |
| 51 | Lecturer with WordPress site | Course site on WordPress | ✅ Works | Standard HTML extraction |
| 52 | Academic with Notion page | Public Notion page | ⚠️ Partial | Notion has unusual HTML structure |
| 53 | TA with GitHub README | Assessment spec on GitHub | ✅ Works | Extracts rendered markdown |
| 54 | Professor with wiki page | Internal wiki (authenticated) | ❌ Fails | **Cannot access login-protected pages** |
| 55 | Lecturer with malformed URL | Pastes broken link | ❌ Fails | Error handling catches this |
| 56 | Academic with localhost URL | Pastes http://localhost | ❌ Fails | Cannot access local servers |
| 57 | Course leader with HTTPS issue | Site with certificate problems | ❌ Fails | Request may fail on SSL errors |
| 58 | Lecturer with redirect chain | URL with multiple redirects | ⚠️ Partial | 10 redirect limit may be hit |
| 59 | Academic with rate-limited site | Site blocks scraping | ❌ Fails | Request may be blocked |
| 60 | TA with Squarespace site | Modern Squarespace course page | ⚠️ Partial | May work but JS-dependent content lost |
| 61 | Professor with Wix site | Course info on Wix | ⚠️ Partial | Wix is very JS-heavy |
| 62 | Lecturer with Substack link | Assessment info on Substack | ✅ Works | Clean HTML extraction |
| 63 | Academic with Medium article | Assessment discussion on Medium | ✅ Works | Standard HTML extraction |
| 64 | Course team with uni CMS | Official uni CMS page | ✅ Works | Usually standard HTML |
| 65 | Lecturer with very long page | Page with 10,000+ words | ⚠️ Slow | May hit API limits |

---

## CATEGORY C: Example File Users (20 personas)

| # | Persona | Scenario | Likely Outcome | Potential Issue |
|---|---------|----------|----------------|-----------------|
| 66 | First-time visitor | Finds examples in README, downloads | ✅ Works | Clear path if they find GitHub |
| 67 | Non-technical academic | Doesn't know how to download from GitHub | ⚠️ Friction | **GitHub UI confusing for non-devs** |
| 68 | Mobile user | Tries to download PDF on phone | ⚠️ Friction | Mobile download + upload clunky |
| 69 | Curious lecturer | Wants to see examples before signing up | ✅ Works | Examples demonstrate tool |
| 70 | Sceptical professor | Downloads vulnerable example, tests | ✅ Works | Gets high score, validates tool |
| 71 | Engaged academic | Downloads resilient example, tests | ✅ Works | Gets low score, sees improvement path |
| 72 | Workshop participant | Instructor shares example links | ✅ Works | Direct links work |
| 73 | Lecturer comparing both | Downloads both, runs both | ✅ Works | Good comparison experience |
| 74 | Academic wanting Word version | Prefers Word over PDF | ⚠️ Friction | **Only PDF examples provided** |
| 75 | Non-English speaker | Wants examples in their language | ❌ Missing | **Examples only in English** |
| 76 | Different discipline | Wants STEM/Arts/Health example | ⚠️ Partial | Examples are generic business/sustainability |
| 77 | Assessment designer | Wants edge case examples | ⚠️ Partial | Only 2 examples (high/low) |
| 78 | Validator | Wants to verify scoring is accurate | ✅ Works | Can compare expected vs actual |
| 79 | Trainer running workshop | Needs multiple examples for exercise | ⚠️ Limited | Only 2 examples available |
| 80 | Manager evaluating tool | Needs quick demo | ✅ Works | Examples serve this purpose |
| 81 | IT testing deployment | Needs test files | ✅ Works | Examples serve as test data |
| 82 | QA tester | Wants to break the tool | ✅ Useful | Examples establish baseline |
| 83 | Academic writing paper | Wants to cite examples | ⚠️ Partial | Examples not formally citable |
| 84 | Consultant | Wants client-ready examples | ⚠️ Partial | Examples are demo quality |
| 85 | L&D professional | Wants corporate/training examples | ❌ Missing | **Examples are HE-focused only** |

---

## CATEGORY D: Edge Cases and Error States (15 personas)

| # | Persona | Scenario | Likely Outcome | Potential Issue |
|---|---------|----------|----------------|-----------------|
| 86 | User with slow internet | Upload times out | ⚠️ Poor UX | No progress indicator for slow uploads |
| 87 | User during API outage | Gemini API down | ❌ Fails | Error message may be unclear |
| 88 | User hitting rate limits | Makes many requests quickly | ❌ Fails | May get API rate limit error |
| 89 | User with no email | Doesn't want to provide email | ❌ Blocked | **Email is required field** |
| 90 | User with fake email | Enters invalid email format | ⚠️ Partial | Basic validation only |
| 91 | User abandoning mid-analysis | Closes browser during processing | ⚠️ Lost | Analysis lost, must restart |
| 92 | User with ad blocker | Aggressive ad blocker | ✅ Works | Should not affect Streamlit |
| 93 | User with JavaScript disabled | Paranoid security settings | ❌ Fails | Streamlit requires JavaScript |
| 94 | User on corporate network | Firewall blocks Streamlit Cloud | ❌ Fails | Cannot access tool |
| 95 | User with screen reader | Accessibility needs | ⚠️ Partial | Streamlit has limited a11y |
| 96 | User with colour blindness | Relies on colour coding | ⚠️ Partial | Score colours may be indistinguishable |
| 97 | User wanting offline use | Wants to run locally | ✅ Possible | README has installation instructions |
| 98 | User on old browser | IE11 or very old browser | ❌ Fails | Streamlit needs modern browser |
| 99 | User expecting saved history | Returns expecting previous results | ❌ Not saved | **No persistent history** |
| 100 | User wanting batch processing | Has 20 assessments to audit | ❌ Not supported | **Must upload one at a time** |

---

## SUMMARY: Critical Issues to Address

### High Priority (blocks significant user groups)

1. **No .doc support** - Only .docx works. Many academics have legacy files.
2. **No .odt support** - LibreOffice users cannot upload directly.
3. **No OCR for scanned PDFs** - Image-based PDFs fail silently.
4. **VLE URLs don't work** - Moodle/Canvas/Blackboard links fail (authenticated).
5. **GitHub examples confusing** - Non-technical users struggle to download.
6. **No corporate/L&D examples** - B2B users have no relevant samples.

### Medium Priority (causes friction)

7. **PDF URL scraping fails** - Direct PDF links don't work via URL input.
8. **No Word examples** - Some users prefer Word over PDF.
9. **No batch processing** - Course teams with multiple assessments.
10. **No saved history** - Users must re-upload to review past results.
11. **Limited discipline examples** - Only business/sustainability topics.
12. **Email required** - Creates barrier for casual testing.

### Low Priority (edge cases)

13. **JavaScript-heavy sites fail** - SPA course pages don't scrape.
14. **Mobile UX clunky** - Works but not optimised.
15. **Accessibility limited** - Screen readers, colour blindness.
16. **Non-English assessments** - Not tested or documented.

---

## README Gaps Identified

1. **Supported formats not clear** - Need to explicitly list .docx (not .doc), PDF (not scanned), etc.
2. **URL limitations not explained** - Users don't know VLE links won't work.
3. **No troubleshooting section** - What to do when things fail.
4. **No corporate/B2B framing** - README is HE-focused but tool has B2B potential.
5. **Example download path unclear** - GitHub raw file links would help.

---

## Recommended README Additions

### New Section: "What Works and What Doesn't"

```markdown
## Supported Inputs

**File Upload:**
- ✅ PDF (text-based, not scanned images)
- ✅ Word (.docx only, not .doc or .odt)

**Text Paste:**
- ✅ Plain text copied from anywhere
- ✅ URLs to public web pages

**What Won't Work:**
- ❌ Scanned PDFs (no OCR)
- ❌ Login-protected pages (Moodle, Canvas, Blackboard)
- ❌ Direct links to PDF files via URL input
- ❌ Older Word formats (.doc) or LibreOffice (.odt)
```

### New Section: "Troubleshooting"

```markdown
## Troubleshooting

**"Could not extract text"**
- If uploading PDF: Check it's not a scanned image. Try selecting text in your PDF viewer.
- If uploading Word: Ensure it's .docx format. Save As .docx if needed.

**"Error fetching URL"**
- The page may require login. Copy the text manually and paste instead.
- The page may use JavaScript. Copy the text manually and paste instead.

**"Results seem inaccurate"**
- Ensure your brief includes enough detail (task, criteria, submission requirements).
- Very short briefs (under 200 words) may not provide enough context.
```
