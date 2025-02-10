import { useEffect, useState } from "react"
import axios from "axios"
import "./deletetable.css"

export const Deletetable = ()=>{
    const [database,setDatabase] = useState([]);
    const [selectdb,setSelectdb] = useState("");
    const [tables,setTables] = useState([]);
    const [selecttable,setSelecttable] = useState("");

    const fetchdatabase = async ()=>{
        try{
            const res = await axios.get("http://localhost:5000/databases",
                { withCredentials:true }
            );
            setDatabase(res.data.database);

        }catch(error){
            console.log(error);
        }
    }

    useEffect(()=>{
        fetchdatabase();
    },[])

    useEffect(()=>{
        if(selectdb){
        fetchtable();
        }
    },[selectdb])

    const fetchtable = async ()=>{
        try{
            const res = await axios.get("http://localhost:5000/table",
                { params:{db:selectdb},
                withCredentials:true }
            )
            console.log(res.message);
            setTables(res.data.tables);
            
        }catch(error){
            console.log("fetch table error",error);
        }
    }

    const deltable = async ()=>{
        try{
            const res = await axios.delete("http://localhost:5000/table",{
                params:{database:selectdb,table:selecttable},
                withCredentials:true,
            })
            console.log("status code : ",res.status);
            setTables(tables.filter((t)=> t !== selecttable));

        }catch(error){
            console.log(error);
        }
    }
    return(
        <>
        <div className="out1">
            <div className="in1">
            <h2>Select Database</h2>
            <select onChange={(e)=>setSelectdb(e.target.value)} value={selectdb}>
                <option value="">Select a database</option>
                { database.map((db,index)=>(
                    <option key={index} value={db}>{db}</option>
                ))}
            </select>
            
            </div>
            {selectdb &&(
                <>
                <div className="in2">
                <h2>Select Table</h2>
                <select onChange={(e)=>setSelecttable(e.target.value)} value={selecttable}>
                    <option value="">Select a table</option>
                    {tables.map((table,index)=>(
                        <option key={index} value={table}>{table}</option>
                    ))}
                </select>
            </div>
            <div className="in3">
                <button onClick={deltable}>Delete</button>
            </div>
            </>
        )}

        </div>
        </>
    )
}