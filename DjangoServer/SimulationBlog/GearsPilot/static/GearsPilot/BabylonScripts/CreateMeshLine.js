
            var pointsArray = [[0,0,0],
                               [0,1,1],
                               [0,2,2],
                               [0,3,3],
                               [0,4,4]];
            var vecArray = [];
            var i = 0;
            for (let arr of pointsArray) {

                vecArray[i] = new BABYLON.Vector3(arr[0],arr[1],arr[2]);
                i++;
            }

            var line = BABYLON.MeshBuilder.CreateLines("line", {points: vecArray}, scene);
