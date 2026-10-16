# F1 Predictor

A minimal Formula 1 head-to-head prediction website backed by a random forest. Enter pre-race feature differences for two drivers to estimate which driver finishes ahead.

The website includes a home page, a comparison form, five historical test examples, and the first tree's decision path. Predictions run entirely in the browser using an exported model; hosting needs no Python backend, API keys, cookies, or sign-in.

## Run locally

Python 3 is enough to serve the included website:

```sh
python3 -m http.server 8080 --directory public
```

Open http://localhost:8080. The comparison tool is at http://localhost:8080/predictor.html. Select **Next example**, then **Predict result** to try a real historical pair.

Serve over HTTP rather than opening the HTML files directly: the app fetches `model.json`.

## Deploy to Vercel

The root `vercel.json` configures a static deployment of `public/`. The model is already exported; no installation or build step is required.

1. Push this repository, including `public/` and `vercel.json`, to your Git provider.
2. In Vercel, select **Add New → Project** and import the repository.
3. Keep the **Root Directory** at the repository root. The framework is **Other**, the output directory is **public**, and install/build commands are empty, as configured in `vercel.json`.
4. Deploy and open the production `https://…vercel.app` URL returned by Vercel.

Alternatively, with Node.js and access to your Vercel account:

```sh
npx vercel login
npx vercel --prod
```

Run these from the repository root. No Vercel deployment has been created by these configuration files alone.

### Access from private/incognito windows

The website's links and model requests are relative to the current host. They do not depend on a ChatGPT session, Vercel login, or browser storage.

In Vercel **Project Settings → Deployment Protection**, ensure the production deployment is accessible to unauthenticated visitors. Preview URLs may have different protection settings; share the production domain. Access protection is an account setting, not something this static `vercel.json` disables.

After deployment, open a new private/incognito window without signing in and verify:

- `/` opens the home page.
- **Compare drivers** opens `/predictor.html`.
- **Next example → Predict result** produces probabilities.
- The **F1 / PREDICTOR** link returns home.
- `/model.json` opens without an authentication prompt.

A website cannot force a link to open an incognito window. Open that window using the browser's menu. The earlier ChatGPT Sites URL is a separate private deployment and does not become public when this project is deployed to Vercel.

References: [Vercel static configuration](https://vercel.com/docs/project-configuration/vercel-json), [deployment protection](https://vercel.com/docs/deployment-protection).

## Model

| Setting | Value |
| --- | --- |
| Trees | 20 |
| Maximum depth | 5 |
| Minimum samples to split | 10 |
| Features per split | Floor of the square root of the feature count |
| Sampling | Bootstrap rows with replacement |
| Random seed | 42 |
| Training seasons | 2014–2024 |
| Holdout season | 2025 |
| Training pairs | 42,835 |
| Holdout pairs | 4,139 |
| Exported forest holdout accuracy | Approximately 76.8% |

Each tree returns the share of label 1 at its reached leaf. The forest averages these shares. Label 1 means Driver A finishes ahead of Driver B. This is historical pairwise classification, not live race forecasting, and probabilities are not calibrated.

`algorithm.py` contains the learning implementation. `frontend/export_model.py` trains a separate, optimized NumPy implementation using cumulative counts for split search and the same forest settings. The website uses that exported forest, not a live call to `algorithm.py`. Different numerical tie handling can produce different trees and metrics.

## Inputs

All differences are **Driver A minus Driver B**.

| Input | Meaning |
| --- | --- |
| Grid difference | Difference in starting positions after preprocessing pit lane starts |
| Pit lane flag difference | Difference between flags: 1 for pit lane start, 0 otherwise |
| Qualifying position difference | Difference in qualifying positions |
| Qualifying sessions difference | Difference in the number of sessions with recorded times |
| Q1 / Q2 / Q3 gap differences | Difference in session gaps to the fastest driver, in percentage points |
| Driver form difference | Difference in average finishing position over each driver's previous five races |
| Team form difference | Difference in rolling team finishing-position averages over the preceding five races |
| Best grid position | Lower of the two processed grid positions |

Leave unknown inputs blank. The frontend fills them with training medians and sets missing indicators where the training schema includes them. Historical examples retain their original missingness. Driver names and current race feeds are not included.

## Training and refreshing the website

The existing Python workflow uses NumPy, pandas, and matplotlib:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install numpy pandas matplotlib
.venv/bin/python algorithm.py
```

Run training from the repository root, where `races.csv`, `results.csv`, and `qualifying.csv` are located. The learning implementation's exhaustive threshold search can be slow.

With the frontend source checkout available, rebuild the optimized browser model and refresh the Vercel files:

```sh
.venv/bin/python frontend/export_model.py
.venv/bin/python prepare_vercel.py
```

Commit the refreshed `public/` files and push to trigger a Vercel redeployment. Vercel does not retrain the model.

## Files

```text
algorithm.py               Learning implementation of the random forest
features.py                CSV loading, preprocessing, and chronological split
frontend/                  Separate frontend Git checkout, when available
prepare_vercel.py          Copies the static frontend export into public/
public/index.html          Deployable home page
public/predictor.html      Browser prediction interface
public/model.json          Exported forest, medians, examples, and metrics
vercel.json                Static Vercel deployment configuration
```

`frontend/` is currently recorded as a Git link in the parent repository. A fresh clone may not contain its files. The ordinary tracked files in `public/` make Vercel deployment independent of that nested checkout. Keep `public/` committed; restoring the frontend checkout is only needed to regenerate the export.
