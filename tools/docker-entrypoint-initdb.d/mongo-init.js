print('######################### Creating DB  ###############################');

db = db.getSiblingDB('test-database')
db.createUser({
  user: 'abc',
  pwd: 'abc',
  roles: [
    {
      role: 'readWrite',
      db: 'dogami-database',
    },
  ],
});


print('######################### DONE ############################');

