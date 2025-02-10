const express = require("express");
const mysql = require("mysql2");
const bodyparser = require("body-parser");
const cors = require("cors");
const session = require("express-session");


const app = express();

app.use(cors(
    {
        origin: "http://localhost:5173", 
        credentials: true,
    }
));
app.use(bodyparser.json());



app.use(
    session({
        secret: "chiyanraja07",
        resave: false,
        saveUninitialized: true,
        
    })
);

app.use((req,res,next)=>{
    res.setHeader("Content-Type","application/json");
    console.log("session data",req.session);
    next();
});

function connecttodatabase(detail,callback){
    if(!detail){
        console.log("Data Missing");
        return callback(false);
    }
    const db = mysql.createConnection({
        host:detail.host,
        user:detail.user,
        password:detail.pass,
    });

    db.connect((err)=>{
        if(err){
            console.log(err);
            callback(false);
        }else{
            console.log("connected");
            
            callback(true,db);
        }
    });
}


app.post("/connect",(req,res)=>{
    
    
    const { host,user,pass } = req.body;
    if(!host || !user || !pass){
        return res.status(400).json({error:"Login Credentials  missing"});
    }
    req.session.conn = { host,user,pass };

    connecttodatabase(req.session.conn,(success)=>{
        if(success){
            
            res.status(200).json({message:"connection successful"});
        }else{
        return res.status(500).json({error:"Invalid Login Credentils"});
        }
    });


});

function check(req,res,next){
    if(!req.session.conn){
        return res.status(400).json({error:"Missing details"});

    }
    next();
}

function createdatabase(db,databasename,callback){
    const query = `CREATE DATABASE  ${databasename}`;
    db.query(query,(err) =>{
        if(err){
            console.log("error creating database",err);
            callback(err);
        }else{
            console.log("connected to database");
            callback(null);
        }
    });
};

function deletedb(db,dbname,callback){
    const query = `DROP DATABASE IF EXISTS ${dbname}`;
    db.query(query,(err)=>{
        if(err){
            console.log("del error");
            return callback(false);
        }
        console.log("deleted");
        callback(true);
    })
}


app.post("/database", check,(req,res)=>{
    const { dataname } = req.body;
    
    console.log("database name : ",dataname);

    if(!dataname){
        return res.status(400).json({error:"Database name is missing"});
    }
    
    connecttodatabase(req.session.conn,(success,db)=>{
        if(success){
            console.log("connected");
            createdatabase(db,dataname,(err)=>{
                if(err){
                    return res.status(500).json({error: err.sqlMessage || "Failed to create database"});
                }
                return res.status(200).json({message:"successfully created database"});
                
                
            })
            
        }else{
            res.status(500).json({error:"failed to create database"});
        }
    });
});

app.get("/databases",check,(req,res)=>{
    console.log("get method"); 
    connecttodatabase(req.session.conn,(success,db)=>{
        if(success){
            fetchdatabase(db,(dbsuccess,dbdata)=>{
                if(dbsuccess){
                    console.log("database : ",dbdata);
                    res.status(200).json({database:dbdata});
                    console.log("if finish");
                }else{
                    res.status(500).json({error:dbdata});
                }

            })
        }else{
            res.status(500).json({error:"failed to connect with database"});
        }
    })
})

app.get("/table",check,(req,res)=>{

    const  dbase  = req.query.db;
    console.log("table database name : ",dbase);
    connecttodatabase(req.session.conn,(success,db)=>{
        if(success){
            db.changeUser({ database:dbase },(err)=>{
                if(err){
                    return res.status(500).json({error:"Failed to switch database"});
                }

                const query = "SHOW TABLES";
                db.query(query,(err,results)=>{
                    if(err){
                        return res.status(500).json({error:"failed to fetch"});
                    }
                    const tables = results.map((row)=>Object.values(row)[0]);
                    return res.status(200).json({tables});
                })
            })
        }else{
            return res.status(500).json({error:"connection unsuccesful"});
        }

    })
})

app.delete("/table",check,(req,res)=>{
    const { database,table } = req.query;
    console.log("table and database : ",database,table);
    if(!database || !table){
        return res.status(400).json({error:"missing table or database"});
    }
    connecttodatabase(req.session.conn,(success,db)=>{
        if(success){
            db.changeUser({ database },(err)=>{
                if(err){
                    return res.status(500).json({error:"database change error"});
                }
                const query = `DROP TABLE ${table}`;
                db.query(query,(err)=>{
                    if(err){
                        return res.status(500).json({error:"Table deletion error"});
                    }
                    return res.status(200).json({message:"Table deletion successfully"});
                })
            })
        }
    })
})

app.get("/column",check,(req,res)=>{
    const {database,table} = req.query;

    connecttodatabase(req.session.conn,(success,db)=>{
        if(!success){
            return res.status(500).json({error:"unable to connect"});
        }
        db.changeUser({database},(err)=>{
            if(err){
                return res.status(500).json({error:"databse change error"});
            }
            const query = `SHOW COLUMNS FROM ${table}`;
            db.query(query,(err,results)=>{
                if(err){
                    return res.status(500).json({error:"unable to fetch columns"});
                }
                const columns = results.map((col)=>col.Field);
                return res.status(200).json({columns});
            })
        })
    })
})

app.post("/join",check,(req,res)=>{
    const {database,table1,table2,col1,col2,join} = req.body;
    connecttodatabase(req.session.conn,(success,db)=>{
        if(!success){
            return res.status(500).json({error:"unable to connect"});
        }
        db.changeUser({database},(err)=>{
            if(err){
                return res.status(500).json({error:"unable to change database"});
            }
            const query = `SELECT * FROM ${table1} ${join} ${table2} ON ${table1}.${col1}=${table2}.${col2}`;
            db.query(query,(err,results)=>{
                if(err){
                    return res.status(500).json({error:"error to join tbles"});
                }
                return res.status(200).json({results});

            })
        })
    })
})

app.post("/insert",check,(req,res)=>{
    const { database,table,data } = req.body;
    const columns = Object.keys(data);
    const values = Object.values(data);

    if(!database || !table || !data){
        return res.status(500).json({error:"details missing"});
    }

    connecttodatabase(req.session.conn,(success,db)=>{
        if(!success){
            return res.status(500).json({error:"unable to connect"});
        }
        db.changeUser({database},(err)=>{
            if(err){
                return res.status(500).json({error:"unable to change database",details:err.message});

            }
            const query = `INSERT INTO ${table} (${columns.join(",")}) VALUES (${columns.map(()=>"?").join(",")})`;
            db.query(query,values,(err,results)=>{
                if(err){
                    return res.status(500).json({error:"unable to insert values"});

                }
                res.status(200).json({message:"Data inserted Successfully",results});
            })
        })
    })
})

function fetchdatabase(db,callback){
    const query = "SHOW DATABASES";
    db.query(query,(err,result)=>{
        if(err){
            console.log("error",err.message);
            callback(false);
        }else{
            const databases = result.map((row)=>row.Database);
            callback(true,databases);
        }

    })
}


app.post("/create_table",check,(req,res)=>{
    const { database,tablename,columnname } = req.body;
    console.log(database);
    console.log(tablename);
    console.log("backend",columnname);

    if(!database || !tablename || !columnname){
        return res.status(400).json({error:"Data missing"});
    }
    connecttodatabase(req.session.conn,(success,db)=>{
        if(!success){
            return res.status(500).json({error:"Failed to connect"});
        }


        db.changeUser({database},(err)=>{
            if(err){
                return res.status(500).json({error:"Failed to switch"});
            }
            const colsql = columnname.map((col)=> `${col.colname} ${col.datatype}`).join(",");

            const createquery = `CREATE TABLE ${tablename} (${colsql})`;

            db.query(createquery,(err)=>{
                if(err){
                    console.log(`log error ${err.sqlMessage}`);
                    return res.status(500).json({error:err.sqlMessage});
                }
                res.status(200).json({message:`Table ${tablename} created succesfully`});
            })

        })
    })
})

app.post("/deldb",check,(req,res)=>{
    const { dbname } = req.body;
    connecttodatabase(req.session.conn,(success,db)=>{
        if(!success){
            return res.status(500).json({error:"Error to connect"});

        }
        deletedb(db,dbname,(delsuccess)=>{
            if(delsuccess){
                res.status(200).json({message:" Database successfully deleted"});
            }else{
                res.status(500).json({error:"unknown error"});
            }
        })
})
})

app.listen(5000,()=>{
    console.log("app running on 5000");
})