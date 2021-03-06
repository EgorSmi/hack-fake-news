import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import {Alert, AlertTitle, Box, Button, Card, LinearProgress, Step, StepLabel, Stepper, TextField} from "@mui/material";
import React, {useEffect, useState} from "react";
import {CheckItem} from "../../types/checkItem";
import {CheckResponse, FindItem} from "../../types/checkResponse";
import {HighLighterComponent} from "../HighlighterComponent";
import {FindListComponent} from "../FindListComponent";
import {SentimentComponent} from "../SentimentComponent";


export const MainComponent = (): JSX.Element => {

    const [activeStep, setActiveStep] = useState(0);
    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');
    const [checkItem, setCheckItem] = useState<CheckItem | undefined>(undefined);
    const [result, setResult] = useState<CheckResponse | undefined>(undefined);
    const [activeItem, setActiveItem] = useState<FindItem | undefined>(undefined)
    const [error, setError] = useState<string>('')
    const steps = ['Статья', 'Проверка', 'Результат проверки'];
    const stepRender = [step1, step2, step3]


    useEffect(() => {
        setCheckItem({title: title, content: content})
    }, [title, content])

    function check() {
        const requestOptions = {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(checkItem)
        };
        setActiveStep(1)
        fetch('/api/check', requestOptions)
            .then((response) => response.json())
            .then((data: CheckResponse) => {
                setActiveStep(2)
                setResult(data);
                console.log(data);
            })
            .catch(() => {
                setError('Попробуйте еще раз.')
            })

    }

    function back() {
        setActiveStep(0)
        setActiveItem(undefined)
        setError('');
    }

    function stepper() {
        return (
            <Stepper activeStep={activeStep} sx={{marginTop: '10px', marginBottom: '10px', width: '100%'}}>
                {steps.map((label, index) => {
                    const stepProps: { completed?: boolean } = {};
                    const labelProps: {
                        optional?: React.ReactNode;
                    } = {};
                    return (
                        <Step key={label} {...stepProps}>
                            <StepLabel {...labelProps}>{label}</StepLabel>
                        </Step>
                    );
                })}
            </Stepper>
        );
    }

    function step1() {
        return (
            <>
                <TextField
                    sx={{width: '100%'}}
                    id="title"
                    label="Заголовок"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                />
                <TextField
                    sx={{width: '100%', marginTop: '20px'}}
                    minRows={10}
                    id="content"
                    label="Статья"
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    multiline
                />
            </>
        );
    }

    function step2() {
        return (
            <Box sx={{width: '100%', marginTop: '10px'}}>

                {(error.length) ? (
                    <Alert severity="error">
                        <AlertTitle>Ошибка</AlertTitle>
                        {error}
                    </Alert>
                ) : (<LinearProgress/>)}
            </Box>
        );
    }

    function verdict(){
        const res = result?.result ?? 0;
        return ((res>=90)?'новость достоверная' :
                        (res>=60)?'скорее всего не фейк' :
                            (res>=40)?'скорее всего фейк' :
                                        'фейк');
    }

    function step3() {
        const res = result?.result ?? 0;
        return (
            <>

                <Typography variant="h6" color="text.secondary" sx={{textAlign: 'left'}} gutterBottom>
                    Результат проверки <strong>{res}% ({verdict()})</strong>
                </Typography>
                <Typography variant="h6">{checkItem?.title ?? ''}</Typography>
                <Box sx={{fontSize: 'initial', border: 1, borderRadius: '5px', padding: '10px', minHeight: '40vh'}}>

                    <HighLighterComponent
                        pattern={activeItem?.pattern ?? checkItem?.content ?? ''}
                        text={''}
                        color="#b5f4b1"
                    />
                </Box>

                <FindListComponent
                    items={result?.items ?? []}
                    onSelectItem={(x) => {
                        setActiveItem((x===activeItem)?undefined:x)
                    }}
                    selectedItem={activeItem}
                    result={result}
                ></FindListComponent>

                {(result?.sentiment) ?
                    (<SentimentComponent sentiment={result.sentiment}></SentimentComponent>)
                    : (<></>)}
            </>

        );
    }

    function actions() {
        return (
            <div style={{marginTop: '10px', display: 'flex', justifyContent: 'space-between'}}>
                <Button onClick={back} disabled={activeStep === 0}>Назад</Button>
                <Button onClick={check} disabled={activeStep !== 0}>Проверить</Button>
            </div>
        );
    }


    return (
        <Card sx={{width: '90vw', minHeight: '80vh', display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
            <CardContent>
                <Typography variant="h5" color="text.secondary" sx={{textAlign: 'center'}} gutterBottom>
                    Сервис проверки фейковых новостей
                </Typography>
                {stepper()}
                <div style={{width: '80vw', minHeight: '60vh'}}>
                    {
                        stepRender[activeStep]()
                    }
                    {actions()}
                </div>
            </CardContent>
        </Card>
    );
}