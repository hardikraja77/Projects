import React from "react";
import "./home.css"
import { useNavigate } from "react-router-dom";


const Home = ()=>{
    const navigate = useNavigate();
    const create = ()=>{
        navigate("/create");
    }

    const createtable = ()=>{
        navigate("/createtable")
    }

    const deletedatabase = ()=>{
        navigate("/deletedatabase");
    }

    const deletetable =()=>{
        navigate("/deletetable");
    }

    const join = ()=>{
        navigate("/joins");
    }

    const insert = ()=>{
        navigate("/insert");
    }

    return(
        <>
        <div className="cen">
        <h1>MySQL Home Page</h1>
        <div className="btn1">
            <button onClick={create}>Create Database</button>
            <button onClick={createtable}>Create Table</button>
            <button onClick={deletedatabase}>Delete Database</button>
            <button onClick={deletetable}>Delete Table</button>
            <button onClick={join}>Joins</button>
            <button onClick={insert}>Insert Values</button>
        </div>
        </div>
        </>
    );
};

export default Home;