import React,{ useState } from "react";
import "./Log.css";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const Log=()=>{
    const [credential,setCredential] = useState({
        host:"",
        user:"",
        pass:"",
    })
    const [msg,setMsg] = useState("");

    const navigate = useNavigate();

    const handlesubmit = async (e)=>{
        if(e) e.preventDefault();
        try{
            const response = await axios.post(`http://localhost:5000/connect`,
                {...credential},
                { withCredentials : true}
            );

            if(response.status === 200){
                navigate("/home");
            }


        }catch(error){
            setMsg(error.response.data.error || "Invalid Credentials");
            console.log("fn error",error.response.data.error);
            setTimeout(()=>{
                window.location.reload();
            },3000);
           
        };

        
    }

    return (
    <>
    <div className="log">
    <h1>MySQL Login</h1>
    <input type="text" placeholder="MySQL HostName" className="inp" onChange={(e)=>setCredential({...credential,host:e.target.value})}></input>
    <input type="text" placeholder="Username" className="inp" onChange={(e)=>setCredential({...credential,user:e.target.value})}></input>
    <input type="text" placeholder="Password" className="inp" onChange={(e)=>setCredential({...credential,pass:e.target.value})}></input>
    <button className="btn" onClick={handlesubmit}>Connect</button>
    {msg &&(
        <h2 className="msg">{msg}</h2>
    )}
    </div>
    </>
    );
};

export default Log;