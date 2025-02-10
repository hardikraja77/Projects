import axios from "axios";
import { useEffect, useReducer, useState } from "react";
import "./insert.css"

function reducer(state,action){
    switch(action.type){
        case actiontypes.setDatabase:
            return {...state, database:action.payload}
        case actiontypes.setSelectdb:
            return {...state, selectdb:action.payload}
        case actiontypes.setTables:
            return {...state,tables:action.payload}
        case actiontypes.setSelecttable:
            return {...state,selecttable:action.payload}

        case actiontypes.setColumn:
            return {...state,columns:action.payload}

    }
}

const actiontypes = {
    setDatabase : "setDatabase",
    setSelectdb : "setSelectdb",
    setTables : "setTables",
    setSelecttable : "setSelecttable",
    setColumn:"setColumn",
    setSelectcolumn : "setSelectcolumn",
}

const initState = {
    database:[],
    selectdb:"",
    tables:[],
    selecttable:"",
    columns:[],
    selectcolumn:"",
}

export const Insert = ()=>{

    const [state,dispatch] = useReducer(reducer,initState);
    const [formdata,setFormdata] = useState({});
    const fetchdatabase = async ()=>{
        try{
            const res = await axios.get("http://localhost:5000/databases",
                { withCredentials:true },
            )
            dispatch({type:actiontypes.setDatabase,payload:res.data.database});
        }catch(error){
            console.log(error);
        }
    }

    useEffect(()=>{
        fetchdatabase();
    },[])

    const fetchtable = async ()=>{
        try{
            const res = await axios.get("http://localhost:5000/table",{
                params:{db : state.selectdb},
                withCredentials : true,
        });
            
            dispatch({type:actiontypes.setTables,payload:res.data.tables})
        }catch(error){
            console.log(error);
        }
    }

    useEffect(()=>{
        if(state.selectdb){
        fetchtable();
        }
    },[state.selectdb])

    const fetchcolumn = async ()=>{
        try{
            const res = await axios.get("http://localhost:5000/column",
                {
                    params:{database:state.selectdb,table:state.selecttable},
                 withCredentials:true }
            )
            console.log(res.data.columns);
            if(Array.isArray(res.data.columns)){
            dispatch({type:actiontypes.setColumn,payload:res.data.columns});
            const initialdata = res.data.columns.reduce((acc,col)=>({...acc,[col]:""}),{});
            setFormdata(initialdata);
            }
        }catch(error){
            console.log(error);
        }
    }

    useEffect(()=>{
        if(state.selecttable){
        fetchcolumn();
        }
    },[state.selecttable])

    const insertval = async ()=>{
        try{
            console.log(formdata);
            const res = await axios.post("http://localhost:5000/insert",
                { database:state.selectdb,
                    table:state.selecttable,
                    data : formdata,
                },
                { withCredentials:true }
            );
            alert(`Data Inserted successfully ${JSON.stringify(res.data.results)}`);
        }catch(error){
            console.log("fn ",error);
        }
    }

    const handlechange = (e,col) =>{
        setFormdata((prev)=>({...prev,[col]:e.target.value }));
    }

    return(
        <>
        <div className="out6">
            <h3>Select a Database</h3>
            <select onChange={(e)=>dispatch({type:"setSelectdb",payload:e.target.value})}>
                <option value="">Select a Database</option>
                {state.database.map((db,index)=>(
                    <option key={index} value={db}>{db}</option>
                ))}
            </select>
            
            {state.selectdb &&(
                <>
                <h3>Select a Table</h3>
                <select onChange={(e)=>dispatch({type:actiontypes.setSelecttable,payload:e.target.value})} value={state.selecttable}>
                <option value="">Select a Table</option>
                {
                    state.tables.map((tab,index)=>(
                    <option key={index} value={tab}>{tab}</option>
                ))}
            </select>
            </>
            )}

            {state.selecttable && state.columns.length > 0 &&(
                <>
                {
                    state.columns.map((col,index)=>(
                
                    <div key={index} className="inscol">
                    <label>{col}</label>
                    <input placeholder="enter" value={formdata[col] || ""} onChange={(e)=>handlechange(e,col)} />
                    </div>

                ))
                }
                </>
                
            )

            }
            <div>
            <button onClick={insertval} className="insbtn">Insert</button>
            </div>
            
        </div>
        
       
        </>
    )
}