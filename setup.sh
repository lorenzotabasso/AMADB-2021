#!/bin/bash
docker-compose up -d

sleep 2

cmd="echo 'rs.initiate({_id: \`"mongorsconf\`", configsvr: true, members: [{ _id : 0, host : \`"mongoconf\`" }]})' | mongo"
docker exec -it mongoconf bash -c $cmd

cmd="echo 'rs.initiate({_id : \`"mongors1\`", members: [{ _id : 0, host : \`"mongoshard1\`" }]})' | mongo"
docker exec -it mongoshard1 bash -c  $cmd

cmd="echo 'rs.initiate({_id : \`"mongors2\`", members: [{ _id : 0, host : \`"mongoshard2\`" }]})' | mongo"
docker exec -it mongoshard2 bash -c  $cmd

sleep 2

cmd="echo 'sh.addShard(\`"mongors1/mongoshard1\`")' | mongo"
docker exec -it mongorouter bash -c $cmd

cmd="echo 'sh.addShard(\`"mongors2/mongoshard2\`")' | mongo"
docker exec -it mongorouter bash -c $cmd

# docker-compose down