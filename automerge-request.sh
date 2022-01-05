#!/bin/sh
# creates MR from `main` to `public-main` when `main` is updated
# creates MR from `public-main` to `main` when `public-main` is updated

if [ $CI_COMMIT_REF_NAME == "main" ]; then
  TARGET_BRANCH="public-main"
elif [ $CI_COMMIT_REF_NAME == "public-main" ]; then
  TARGET_BRANCH="main"
fi

TITLE="${CI_COMMIT_REF_NAME}%20to%20${TARGET_BRANCH}%20SYNC"

# Get all open merge requests and check if one exists for source branch
LISTMR=`curl -L --silent "https://${CI_SERVER_HOST}/api/v4/projects/${CI_PROJECT_ID}/merge_requests?state=opened" --header "PRIVATE-TOKEN:${PROJECT_ACCESS_TOKEN}"`;
COUNTBRANCHES=`echo ${LISTMR} | grep -o "\"source_branch\":\"${CI_COMMIT_REF_NAME}\"" | wc -l`;

# If no MR found, create a new one
if [ ${COUNTBRANCHES} -eq "0" ]; then
  curl -L --request POST "https://${CI_SERVER_HOST}/api/v4/projects/${CI_PROJECT_ID}/merge_requests?id=${CI_PROJECT_ID}&source_branch=${CI_COMMIT_REF_NAME}&target_branch=${TARGET_BRANCH}&title=${TITLE}&remove_source_branch=false&assignee_id=${GITLAB_USER_ID}" --header "Content-Type:application/json" --header "PRIVATE-TOKEN:${PROJECT_ACCESS_TOKEN}"
  echo "Opened a new merge request: ${TITLE} and assigned to ${GITLAB_USER_NAME}";
  exit;
fi

echo "No new merge request opened. Merge Request already exists";
