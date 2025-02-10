import { useState } from "react"
import "./Createdatabase.css"
import axios from "axios";

export const Createdatabase = ()=>{
    const [database,setDatabase] = useState("");
    const [msg,setMsg] = useState("");
    const time = ()=>{
        setTimeout(()=>{
            window.location.reload();
        },3000);
    }
    const create = async (e)=>{
        if(e) e.preventDefault();
        try{
            const res = await axios.post(`http://localhost:5000/database`,{
                dataname:database,
            },{ withCredentials : true
            });
            
            setMsg(res.data.message || `Database ${database} Created Successfully`);
            console.log("res",msg);
            time();
        }catch(error){
            setMsg(error.response.data.error || "Error Creating Database");
            console.log(" fn error",error);
            time();
        }
    }

    const enter =(e)=>{
        if(e.key === "Enter"){
            create();
            
        }
    }
    return(
        <>
        <div className="tot">
        <h1>Create Database</h1>
        <div className="inp1">
            <label>Enter Database Name</label>
            <input placeholder="Enter a Name" onChange={(e)=>{setDatabase(e.target.value)}} onKeyDown={enter} ></input>
            <button onClick={create}>Create</button>
        </div>
        
        {
            <h2 className="msg">{msg}</h2>
            
        }
        
        </div>
        </>
    )
}