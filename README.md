# Flask Application Setup and Run

## Setting Up the Environment

1. **Clone the repository:**

    ```bash
    git clone https://github.com/your-repo/flask_app.git
    cd flask_app
    ```

2. **Run the setup script:**

    ```bash
    ./scripts/setup_env.sh
    ```

    This script will create a virtual environment and install the necessary dependencies.

## Running the Application

1. **Start the Flask application:**

    ```bash
    ./scripts/run_flask.sh
    ```

    This script will set up the environment variables and start the Flask server.

## Environment

THE PRODUCTION ENVIRONMENT IS HOSTED ON AMAZON ELASTIC BEANSTALK
THE STORAGE IS S3
THE DATABASE IS HOSTED ON SUPABASE POSTGRES
THE LANDING PAGE IS HOSTED ON UNICORNPLATFORM
DEPLOYMENTS ARE LAUNCHED FROM CIRCLECI
