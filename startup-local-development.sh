# bash
echo "stopping services"
docker-compose stop
echo "taking down services"
docker-compose down --rmi all -v
echo "rebuilding"
docker-compose build
docker-compose up --no-start

echo "bringing up services"
docker-compose start postgres hasura

echo "waiting for hasura"
until [[ "$(curl --silent --fail http://localhost:8082/v1/version)" == *"version"* ]]; do
    printf '.'
    sleep 5
done

echo "applying seeds"
cd hasura/
hasura seeds apply
cd ..

cd flask
export PYTHONPATH=$PYTHONPATH:"$(pwd)"
pip3 install -r requirements.txt
flask run --port 8050
