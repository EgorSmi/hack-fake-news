import React from "react";
import {FindItem} from "../../types/checkResponse";
import {Box, Button, List, ListItem, ListItemButton, ListItemIcon, ListItemText} from "@mui/material";
import {Link} from "@mui/icons-material";

interface FindListInterface {
    items: FindItem[]
    selectedItem:FindItem | undefined
    onSelectItem: (item: FindItem) => void
}


export const FindListComponent = (
    {items,onSelectItem,selectedItem}: FindListInterface): JSX.Element => {

    function renderItems(){
            return items.map((item,i)=>{
                return (
                    <ListItem disablePadding key={i} sx={{
                        borderRadius:'40px',
                        backgroundColor:selectedItem==item?"#b5f4b1":"#ededed"}}>
                    <ListItemButton onClick={()=>{onSelectItem(item)}}>
                        <ListItemText primary={item.name}/>
                        <ListItemIcon onClick={()=>{ window.open(item.href, '_blank', 'noopener,noreferrer');}}>
                            <Link/>
                        </ListItemIcon>
                    </ListItemButton>
                </ListItem>
                )
            })
    }

    return (
        <Box>
            <List>
                {renderItems()}
            </List>
        </Box>
    )
}