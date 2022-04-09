docker_command="docker-compose --env-file .env.production"

if [ $# -ne 1 ]
  then
    echo "Please supply one command for docker-compose"
    echo "Usage: sh deploy.sh <command>"
    echo "<command>: up/down/restart/build .."
    exit
fi

echo "Running: ''$docker_command $1''" 
$docker_command $1

# Why do we need this --env-file option?
# https://stackoverflow.com/a/39548957/18616317
