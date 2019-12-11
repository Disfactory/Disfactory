apt-get install -y binutils libproj-dev gdal-bin
pip3 install pipenv && cd backend && pipenv install --system && cd ..
ln -s backend/manage.py ./manage.py

