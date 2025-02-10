import { useEffect, useState } from "react"
import axios from "axios";
import "./joins.css"

export const Joins = ()=>{
    const [database,setDatabase] = useState([]);
    const [tables,setTables] = useState([]);
    const [selectdb1,setSelectdb1] = useState("");
    const [selecttable1,setSelecttable1] = useState("");
    const [selecttable2,setSelecttable2] = useState("");
    const [columns1,setColumns1] = useState([]);
    const [columns2,setColumns2] = useState([]);
    const [selectcol1,setSelectcol1] = useState("");
    const [selectcol2,setSelectcol2] = useState("");
    const [selectjoin,setSelectjoin] = useState("")
    const [showtables,setShowtables] = useState([]);
    const [headers,setHeader] = useState([]);

    const fetchdatabase = async ()=>{
        try{
            const res = await axios.get("http://localhost:5000/databases",
                { withCredentials:true },   
            )
            setDatabase(res.data.database);
        }catch(error){
            console.log(error);
        }
    }

    const fetchtable = async ()=>{
        try{
            const res = await axios.get("http://localhost:5000/table",{
                params:{db:selectdb1},
                withCredentials:true,
            })
            setTables(res.data.tables);
            return
        }catch(error){
            console.log(error);
        }
    }

    const fetchcolumn = async (selecttable,col)=>{
        try{
            const res = await axios.get("http://localhost:5000/column",{
                params:{database:selectdb1,table:selecttable},
                withCredentials:true,
            })
            if(col===1){
            setColumns1(res.data.columns);
            }
            if(col===2){
                setColumns2(res.data.columns);
            }

        }catch(error){
            console.log(error);
        }
    }

    useEffect(()=>{
        if(database){
        fetchdatabase();
        }
    },[])

    useEffect(()=>{
        if(selectdb1){
        fetchtable();
        }
    },[selectdb1])

    useEffect(()=>{
        if(selecttable1){
        fetchcolumn(selecttable1,1);
        }

    },[selecttable1]);

    useEffect(()=>{
        if(selecttable2){
            fetchcolumn(selecttable2,2);
        }
    },[selecttable2])


    const join = async ()=>{
        try{
            const res = await axios.post("http://localhost:5000/join",
                {database:selectdb1,table1:selecttable1,table2:selecttable2,col1:selectcol1,col2:selectcol2,join:selectjoin},
                { withCredentials:true }
            )
            console.log(res.data.results);
            setShowtables(res.data.results);
            if(showtables.length>0){
            setHeader(Object.keys(showtables[0]));
            }

        }catch(error){
            console.log(error);
        }
    }
    return(
        <>
        <div className="out4">
        <div className="">
            <div>
                <div>
            <h3>Select database</h3>
            </div>
            <select onChange={(e)=>setSelectdb1(e.target.value)} value={selectdb1}>
                <option>Select a database</option>
                {database.map((db,index)=>(
                    <option key={index} value={db}>{db}</option>
                ))}
            </select>
            </div>
            <div>
            {
                selectdb1 &&(
                <>
                <h3>Select Table</h3>
                <select onChange={(e)=>setSelecttable1(e.target.value)} value={selecttable1}>
                <option value="">Select a table</option>
                    {
                        
                        tables.map((t,index)=>(
                            <option key={index} value={t}>{t}</option>
                        ))
                    }
                </select>
                </>
            )}
            </div>
            <div>
            {selecttable1 &&(
                <>
                <div>
                    <h3>Select Column to join</h3>
                    <select onChange={(e)=>setSelectcol1(e.target.value)} value={selectcol1}>
                        <option value="">Select a Column</option>
                        {
                        columns1.map((col,index)=>(
                            <option key={index} value={col}>{col}</option>
                        ))
                        }
                    </select>
                </div>
                </>
            )}
            </div>
            <div>
            {
                selectdb1 &&(
                <>
                <select onChange={(e)=>setSelecttable2(e.target.value)} value={selecttable2}>
                <option value="">Select a table</option>
                    {
                        
                        tables.map((t,index)=>(
                            <option key={index} value={t}>{t}</option>
                        ))
                    }
                </select>
                </>
            )}
            </div>
            <div>
            {selecttable2 &&(
                <>
                <div>
                    <h3>Select Column to join</h3>
                    <select onChange={(e)=>setSelectcol2(e.target.value)} value={selectcol2}>
                        <option value="">Select a Column</option>
                        {
                        columns2.map((col,index)=>(
                            <option key={index} value={col}>{col}</option>
                        ))
                        }
                    </select>
                </div>
                </>
            )}
            </div>

            

        </div>
        <div>
            <div>
            <select onChange={(e)=>setSelectjoin(e.target.value)} value={selectjoin}>
                <option value="">select type of join</option>
                <option value="INNER JOIN">INNER JOIN</option>
                <option value="LEFT JOIN">LEFT JOIN</option>
                <option value="RIGHT JOIN">RIGHT JOIN</option>
            </select>
            </div>
        </div>
        <div className="joinbtn">
        {
            selectdb1 &&(
                <>
                <button onClick={join}>Join Table</button>
                </>
            )
        }
        </div>
        </div>
        <div>
        {
        showtables.length > 0 &&(
            <div className="tab">
            <table border="1" className="tab1">
                <thead>
                    <tr>
                        {headers.map((head,index)=>(
                            <th key={index}>{head}</th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {showtables.map((row,index1)=>(
                        <tr key={index1}>
                            {headers.map((head,colindex)=>(
                                <td key={colindex}>{row[head]}</td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
            </div>
        )}
        </div>
        
        </>
    )
}