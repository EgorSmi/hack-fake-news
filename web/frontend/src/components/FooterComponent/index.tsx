import React from 'react';
import {Card} from '@mui/material';
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";

function Index() {
    return (
        <Card sx={{height: 100,width:'90%',marginTop:'10px'}}>
            <CardContent>
                <Typography sx={{fontSize: 14}} color="text.secondary" gutterBottom>

                </Typography>
            </CardContent>
        </Card>

    );
}

export default Index;
