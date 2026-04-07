# MzansiWins Build Scripts

Python build pipeline that generates the static HTML site from `mzansiwins/src/data.json`.

## Build

```bash
pip install rcssmin rjsmin Pillow
python3 build_site.py
cp mzansiwins-html/assets/style.css.bak mzansiwins-html/assets/style.css
python3 post_build.py
python3 -c "import rcssmin; open('mzansiwins-html/assets/style.css','w').write(rcssmin.cssmin(open('mzansiwins-html/assets/style.css.bak').read()))"
```

Built output goes to `mzansiwins-html/` and is deployed to the `main` branch.
