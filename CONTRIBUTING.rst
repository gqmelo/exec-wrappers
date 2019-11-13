============
Contributing
============

Here's how to set up `exec-wrappers` for local development:

1. Fork the `exec-wrappers` repo on GitHub.
2. Clone your fork locally and install flake8 pre-commit hook

.. code-block:: bash

    git clone https://github.com/your_name_here/exec-wrappers.git
    cd exec-wrappers
    flake8 --install-hook=git
    git config --local flake8.strict true

3. Create a new virtualenv environment for developing

.. code-block:: bash

    virtualenv -p python2.7 venv
    source venv/bin/activate  # If using bash, otherwise use the appropriate activate script
    pip install -r requirements.txt

4. Create a branch for local development

.. code-block:: bash

    git checkout -b name-of-your-bugfix-or-feature

Now you can make your changes locally.

5. After each change make sure the tests still pass

.. code-block:: bash

    pytest tests


6. Commit your changes and push your branch to GitHub

.. code-block:: bash

    black .
    git add .
    git commit -m "Your detailed description of your changes."
    git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Tips
----

To run a specific test:

.. code-block:: bash

    pytest tests -k test_name

Sometimes is very useful to see a coverage report to check if you are forgetting
to test something. To generate an html report:

.. code-block:: bash

    pytest --cov exec_wrappers --cov-config .coveragerc --cov-report html tests
