#!/bin/bash

#
# Initialize a new project.
#
# This script prompts you to name your project and provide some additional information,
# then it does a full-text find-replace for the following:
#
#  - {project_name_capitalcase} - The project name in CapitalCase
#  - {project_name} - The lower-cased project name
#  - {project_name_upper} - The project name in all UPPERCASE
#  - {staging_full_url} - The complete URL for this projects staging environment
#  - {database_name} - Default DB name to use with the app. Updates .env.example.
#  - {database_user} - Default DB user to use with the app. Updates .env.example.
#  - {database_password} - Default DB user to use with the app. Updates .env.example.
#  - {storage_hash} - A random string generated for Vuex persisted state.
#

#
# Prompt for project name and other info
#
echo
echo "✨ Let's strap some boots! ✨"
echo

echo "📝 PROPER NAME"
echo "Provide a proper capital-cased name for the project (ex: Soil Nerd)."
echo -n "Then press [ENTER]: "
read project_name_capitalcase

# Generate a suggested project name based on the proper name
auto_project_name="${project_name_capitalcase// /}"
auto_project_name="${auto_project_name,,}"

echo
echo "📝 PACKAGE NAME"
echo "Provide the package name for this app as one lowercase word."
echo "(ex: soilnerd). This will be used to name both front and back"
echo -n "end packages. Then press [ENTER]: "
read -i "${auto_project_name}" -e project_name

# Generate a suggested URL for staging
auto_staging_url="https://staging.${project_name}.com"

echo
echo "📝 FULL STAGING URL"
echo "Provide a complete URL for the staging environment (ex: https://staging.myapp.com)"
echo -n "and press [ENTER]: "
read -i "${auto_staging_url}" -e staging_full_url

echo
echo "📝 DATABASE NAME"
echo "Provide a name for the database [default=${project_name}_db]."
echo -n "Then press [ENTER]: "
read -i "${project_name}_db" -e database_name

echo
echo "📝 DATABASE USER"
echo "Provide a name for the database user [default=${project_name}]."
echo -n "Then press [ENTER]: "
read -i "${project_name}" -e database_user

echo
echo "📝 DATABASE PASSWORD"
echo "Provide a password for the database user [default=${project_name}]."
echo -n "Then press [ENTER]: "
read -i "${project_name}" -e database_password

# Generate random 10-character storage hash for Vuex
storage_hash=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 10 | head -n 1)

#
# Begin File Manipulation
#

# Find-replace {project_name_capitalcase} in all project files.
find ./ -type f \
  ! -name initialize.sh \
  -exec sed -i "s/{project_name_capitalcase}/$project_name_capitalcase/g" {} \;

# Find-replace {project_name} in all project files.
find ./ -type f \
  ! -name initialize.sh \
  -exec sed -i "s/{project_name}/$project_name/g" {} \;

# Rename directories using the project_name
mv server/project_name "server/$project_name"

# Find-replace {project_name_upper} in all project files.
find ./ -type f \
  ! -name initialize.sh \
  -exec sed -i "s/{project_name_upper}/${project_name^^}/g" {} \;

# Initialize the server's .env file from the example .env file
cp -rf server/config/.env.example server/.env

# Initialize the client's .env.local file from the example .env file
cp -rf client/.env.example client/.env.local

# Find-replace {database_name} in all project files.
find ./ -type f \
  ! -name initialize.sh \
  -exec sed -i "s/{database_name}/$database_name/g" {} \;

# Find-replace {database_user} in all project files.
find ./ -type f \
  ! -name initialize.sh \
  -exec sed -i "s/{database_user}/$database_user/g" {} \;

# Find-replace {database_password} in all project files.
find ./ -type f \
  ! -name initialize.sh \
  -exec sed -i "s/{database_password}/$database_password/g" {} \;

# Find-replace {storage_hash} in all project files.
find ./ -type f \
  ! -name initialize.sh \
  -exec sed -i "s/{storage_hash}/$storage_hash/g" {} \;
