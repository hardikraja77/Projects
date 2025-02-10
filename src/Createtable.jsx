import axios from "axios";
import { useEffect, useState } from "react"
import "./createtable.css"



export const Createtable = ()=>{
    const [database,setDatabase] = useState([]);
    const [selecteddatabase,setSelecteddatabase] = useState("");
    const [section,setSection] = useState([]);
    const [tbname,setTbname] = useState("");
    const [msg,setMsg] = useState("");

    useEffect(()=>{
        const fetchdatabase = async ()=>{
            try{
                const res = await axios.get("http://localhost:5000/databases",
                    { withCredentials:true }
                )

                setDatabase(res.data.database);
                console.log(database);
            }
            catch(error){
                console.log("error",error);
            }
        };
        fetchdatabase();
    },[]);

    const addsection = ()=>{
        setSection([
            ...section,
            {colname: "",datatype:""}

        ])
    }

    const handleinp = (index,val)=>{
        const updatesec = [...section];
        updatesec[index].colname = val;
        setSection(updatesec);
    }

    const handleopt = (index,val)=>{
        const updatesec = [...section];
        updatesec[index].datatype = val;
        setSection(updatesec);
    }

    const removesec = (index)=>{
        const updatesec = section.filter((_,i)=> i !== index);
        setSection(updatesec);
    }

    const time = ()=>{
        setTimeout(()=>{
            window.location.reload();
        },5000);
    }

    const createtable = async ()=>{
        try{
            const res = await axios.post(
                "http://localhost:5000/create_table",
                {
                    database:selecteddatabase,
                    tablename:tbname,
                    columnname:section,
                },
                { withCredentials : true}
            )
            
            setMsg(res.data.message);
            time();
            
            
        }catch(error){
            setMsg(error.response.data.error);
            time();
            console.log("fn error",error.response.data.error);
        }
    }
    return(
        <>
        <div className="out">
            <div className="ct">Create Table</div>
            <div className="in">
                <label>Select Database</label>
                <select value={selecteddatabase} onChange={(e)=>setSelecteddatabase(e.target.value)} className="sel">
                    <option>--select a database</option>
                    {database.map((db,index)=>(
                        <option key={index} value={db}>{db}</option>
                    ))}
                </select>
                
                <input placeholder="Enter a Table Name" className="inp2" onChange={(e)=>setTbname(e.target.value)}></input>

                <div>
                    {section.map((sec,index)=>(
                        <div key={index}>
                            <input type="text" placeholder={`Enter colname ${index+1}`} value={sec.colname} onChange={(e)=>handleinp(index,e.target.value)} className="inp2"></input>
                            <select value={sec.datatype} onChange={(e)=>handleopt(index,e.target.value)}>
                                <option value="">--Select a Datatype</option>
                                <option value="INT">INT</option>
                                <option value="VARCHAR(255)">VARCHAR</option>
                                <option value="FLOAT">FLOAT</option>
                                <option value="DOUBLE">DOUBLE</option>
                                <option value="DATE">DATE</option>
                            </select>
                            <button onClick={()=>removesec(index)} className="rmbtn">Remove Column</button>
                        </div>
                    ))}
                </div>
                
                </div>
                <button onClick={addsection} className="btn2">Add Column</button>
                <button onClick={createtable} className="btn2">Create Table</button>
                <div className="msg">
            {
                <h2>{msg}</h2>
            }
        </div>
            </div>
            
            <div>
            
            </div>
            
        </>
    )
}