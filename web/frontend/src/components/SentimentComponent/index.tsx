import React from "react";
import {Sentiment} from "../../types/checkResponse";
import {Box} from "@mui/material";
import Typography from "@mui/material/Typography";

interface SentimentInterface {
    sentiment: Sentiment
}

export const SentimentComponent = ({sentiment}: SentimentInterface): JSX.Element => {

    return (
        <>
            <Box sx={{marginTop:'10px'}}>
                <Typography variant="h6" color="text.secondary" sx={{textAlign: 'left'}} gutterBottom>
                    Тональность текста
                </Typography>
                <Box sx={{margin: "10px"}}>
                    <Typography>Позитивная 😁 <strong>{Math.round((sentiment.positive ?? 0) * 100)}</strong>%</Typography>
                    <Typography>Нейтральная 😐 <strong>{Math.round((sentiment.neutral ?? 0) * 100)}</strong>%</Typography>
                    <Typography>Негативная 😡 <strong>{Math.round((sentiment.negative ?? 0) * 100)}</strong>%</Typography>

                </Box>
            </Box>
        </>
    )
}