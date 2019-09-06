# QualtricsListener -- MVP v1.0
Poor labor conditions, including low wages, unpaid overtime, and abusive employee management environments have all contributed to a systemic pattern of labor violations across the textile industry. However, a growing number of companies are dedicating themselves resolving factory worker issues by developing widespread and deeply impactful wellness programs for their contracted factory workers. Major retailers can employ over 140K factory workers and have more than 70 factories within their production effort, and they have historically strived toward holistic employee health and wellness.

The following repository seeks to provide an open source solution that can be appended to ongoing worker wellness surveying and grievance collection efforts facilitated at a manufacturing factories. The solution will need to accomplish the following:

1. Anonymization of survey responses: Employees’ identity and privacy will be protected.
2. Immutable Reporting: Self-reported employee data will be secure and free from external manipulation.
3. Data Accessibility: Stakeholders throughout the supply chain (including workers, factory managers and leadership, supplier companies, and retailers), and possibly predetermined external stakeholders, will be able to access survey results. This will empower workers, while providing the employer data to better serve workers’ needs.
4. Scalability: The solution will be designed in such a way that it can be scaled quickly beyond the retailer supply chain, making it possible for the survey to establish itself as a universal benchmark and communicate how businesses impact their employees’ well-being.

## Repository Breakdown
In this implementation, the survey will need to leverage the Qualtrics platform, which provides for a Python and JAVA programming interfaces within their new survey response export API, and additionally provides support for R and NodeJS in their legacy v3 export API. The following repository, which is the MVP v1 iteration of the survey listener, will leverage the Python 3 (newest) Qualtrics API in an effort to address gaps in functionality that the newer API has yet to address.

The customized API will have two parts:

1. Survey Listener Service (SLS): An Python 3-based AWS Elastic Beanstalk service that watches for new survey responses being submitted, and upon recognizing new responses, makes a call to our Smart Contract API

2. Smart Contract API (SCA): A NodeJS-based Smart Contract API that, once it receives a POST call from the SLS, commits the data to the PostgreSql database and hashes the survey response to our smart contract. The SCA will be comprised of the following components

This repository fulfills the first part of the solution. The second part can be found here: https://github.com/ConsenSys/WorkerWellnessAPI

## Application Folder Structure
The  has the following folder structure:

    .
    ├── .git               # git build folder
    │   └── ...                           
    ├── .env               # not included in repository, but holds special parameters for qualtrics API   
    ├── .gitignore         # tells github to ignore certain files and folders (.env, and node_modules)  
    ├── application.py     # main script folder making api calls and then relaying data to smart contract api
    ├── utils.py           # helper function
    ├── requirements.txt   # tells ebs which modules are needed in python for script to work
    └── ...

## Developer Team Deployment Steps
1. Git clone the repository into a folder of your choice
2. Attain the .env file that has the project secrets and put .env file in root folder of project
3. Open up your terminal and change directory into the project folder of the repository
4. Make sure that you are listening/processing the correct survey. There are three (2018_REAL_SURVEY_ID, 2017_REAL_SURVEY_ID, 2019_REAL_SURVEY_ID). This variable needs to be set on line 438 where application.py is setting "QUALTRICS_SURVEY_ID" variable in the try statement.
4. Execute the following command in your terminal: python3 application.py
5. The script will be done once it restarts and signals that is it waiting for 300 seconds (for next iteration)
6. MAKE SURE TO DELETE THE QUALTRICS DOWNLOAD AND PYCACHE FOLDERS BEFORE EXECUTING ANOTHER SURVEY.

## How to Set Up the Script
1. Create a qualtrics account or sign up in your existing account. Remember, in order to access their API service you must have an upgraded account.

2. Find your profile image in the top right corner of the page and select "Account Settings"

3. Find your Survey ID next to the survey of your choice in the Survey table (this is your QUALTRICS_SURVEY_ID)

4. Generate a new Token to find your Access Token (this is your QUALTRICS_API_TOKEN)

5. In the url of your profile, find the QUALTRICS_DATA_CENTER id. Read more on how to find the QUALTRICS_DATA_CENTER id in your profile url: https://api.qualtrics.com/docs/root-url

6. Create an .env file with your QUALTRICS_API_TOKEN, QUALTRICS_SURVEY_ID, and QUALTRICS_DATA_CENTER values set

7. Deploy the script using the commands 'npm run build' and 'npm start to fire the script

## Using a Virtual Environment
Once you have the prerequisites installed, set up a virtual environment with virtualenv to install your application's dependencies. By using a virtual environment, you can discern exactly which packages are needed by your application so that the required packages are installed on the EC2 instances that are running your application.

To set up a virtual environment

1. Open a command-line window and type:

```
virtualenv -p python3.7 /tmp/eb_qualtrics_listener_v1
```
Replace 'v1' with the current version listed in the description of the repository. The virtualenv command creates a virtual environment for you and prints the results of its actions:

```
Running virtualenv with interpreter /usr/bin/python3.7
New python executable in /tmp/eb_qualtrics_listener_v1/bin/python3.7
Also creating executable in /tmp/eb_qualtrics_listener_v1/bin/python
Installing setuptools, pip...done.
```

2. Once your virtual environment is ready, start it by running the activate script located in the environment's bin directory. For example, to start the eb_qualtrics_listener_v1 environment created in the previous step, you would type:

```
. /tmp/eb_qualtrics_listener_v1/bin/activate
```
The virtual environment prints its name (for example: (eb_qualtrics_listener_v1)) at the beginning of each command prompt, reminding you that you're in a virtual Python environment. Once created, you can restart the virtual environment at any time by running its activate script again.


## Create an Elastic Beanstalk Environment
1. Install the [EBS CLI](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install.html) on your local computer operating system

2. Open your terminal and change directory into the folder that holds this script

3. Create a repository with the eb init command:
~~~~
~/QualtricsScript$ eb init --platform python --region us-west-2
Application QualtricsScript has been created.
~~~~

4. Create an environment running a sample application with the eb create command:
~~~~
~/QualtricsScript$ eb create --sample QualtricsScript
~~~~

5. Add a configuration file that sets the Node Command to "npm start" in the "QualtricsScript/.ebextensions/nodecommand.config" file path

6. Stage the files - Before doing so, make sure your gitignore file is temporarily deleted, as you will need the ignored files stored on the EBS environment for the script to work. Replace the gitignore file after deploying:
~~~~
~/QualtricsScript$ git add .
~/QualtricsScript$ git commit -m "Updating Qualtrics watcher script - first commit"
~~~~

7. Deploy the changes - replace gitignore file:
~~~~
~/QualtricsScript$ eb deploy
~~~~

## Configuring a Python project for Elastic Beanstalk
You can use the Elastic Beanstalk CLI to prepare your Python applications for deployment with Elastic Beanstalk.

To configure a Python application for deployment with Elastic Beanstalk

1. From within your virtual environment, return to the top of your project's directory tree (python_eb_app), and type:
~~~~
pip freeze >requirements.txt
~~~~

2. This command copies the names and versions of the packages that are installed in your virtual environment to requirements.txt, For example, if the PyYAML package, version 3.11 is installed in your virtual environment, the file will contain the line:
~~~~
PyYAML==3.11
~~~~

3. This allows Elastic Beanstalk to replicate your application's Python environment using the same packages and same versions that you used to develop and test your application.

4. Configure the EB CLI repository with the eb init command. Follow the prompts to choose a region, platform and other options. For detailed instructions, see [Managing Elastic Beanstalk Environments with the EB CLI](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-getting-started.html).

By default, Elastic Beanstalk looks for a file called application.py to start your application. If this doesn't exist in the Python project that you've created, some adjustment of your application's environment is necessary. You will also need to set environment variables so that your application's modules can be loaded. See Using the AWS Elastic Beanstalk Python Platform for more information.


## Additional Resources
You can access Qualtrics documentation here: https://api.qualtrics.com/reference/create-response-export

## Additional Repositories
Additional repositories that are critical to the proof of concept can be found below:

- Smart Contract API: https://github.com/ConsenSys/WorkerWellnessAPI
