[![npm version](http://img.shields.io/npm/v/@illumidesk/jupyter-lti.svg?style=flat)](https://npmjs.org/package/@illumidesk/jupyter-lti 'View this project on npm')

# JupyterLab LTI Extension

IllumiDesk's Canvas LMS assignment submission and assignment reset buttons.

## Installation

```bash
jupyter labextension install @illumidesk/jupyter-lti
```

Once installed you can [enable or disable extensions](https://jupyterlab.readthedocs.io/en/stable/user/extensions.html#installing-extensions).

## Development

For a development install (requires npm version 4 or later), do the following in the repository directory:

- Install and activate conda environment

```bash
  wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O ~/miniconda.sh;
  bash ~/miniconda.sh -b -p $HOME/miniconda
  export PATH="$HOME/miniconda/bin:$PATH"
  pip install --pre jupyterlab
```

- Install dependencies

```bash
npm install
npm run build
jupyter labextension install .
```

(Optional) Watch files as they are changed:

```bash
npm run watch
```

Then launch JupyterLab using:

```bash
jupyter lab --watch
```

This will automatically recompile @illumidesk/jupyter-lti upon changes, and JupyterLab will rebuild itself. You should then be able to refresh the page and see your changes.

```bash
jupyter lab
```

## Integration with LTI Compatible LMS

- Make sure you are authenticated to the LTI compatible LMS (currently only tested with the [Canvas LMS](https://www.canvaslms.com/)) and that you launch a JupyterLab instance from Canvas.

Only users with the `Student` role are able to see the extension and submit an assignment to the Canvas LMS.

[These help docs](https://docs.illumidesk.com) contain more information about the Canvas LMS and IllumiDesk configuration steps.

# Version Control

- `npm version major | minor | patch` update npm version automatically (avoids having to manually update package.json)
