import React, { useEffect, useState } from "react"
import axios from "axios";
import "./deletedatabase.css"

export const Deletedatabase = ()=>{
    const [database,setDatabase] = useState([]);
    const [selectdb,setSelectdb] = useState("");
    const [msg,setMsg] = useState("");

    const fetchdatabase1 = async ()=>{
        try{
            const res = await axios.get("http://localhost:5000/databases",
                { withCredentials:true }
            )
            setDatabase(res.data.database);
            console.log(database);
        }catch(error){
            console.log("fetch error : ",error);
        }
    }

    useEffect(()=>{
        fetchdatabase1();
        
    },[])

    const deldb = async ()=>{
        try{
            const res = await axios.post("http://localhost:5000/deldb",
                {dbname:selectdb},
                { withCredentials:true }
            );

            setMsg(res.data.message);
            
            setSelectdb("");
            setTimeout(()=>{
                window.location.reload();
            },5000)

        }catch(error){
            setMsg(error.response.data.error);
            console.log("del error ",error);
        }
    }

    return(
        <>
        <div className="outdiv">
        <div className="msg">
        <h1>Delete Database</h1>
        </div>
        <div className="cont">
            <h3>Select database</h3>
            <select onChange={(e)=>(setSelectdb(e.target.value))} value={selectdb} className="sel">
            <option value="">Select a database</option>
                {database.map((db,index)=>(
                    
                    <option key={index} value={db}>{db}</option>
                ))}
            </select>
         
        </div>
        <div className="delbtn">
            <button onClick={deldb}>Delete</button>
        </div>
        {
            <div className="msg">
            <h2>{msg}</h2>
            </div>
        }
        </div>
        </>
    )
}