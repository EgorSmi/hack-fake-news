import React from 'react';
import {
    Box,
    Button,
    Card,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle,
    TextField
} from '@mui/material';
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";


function Index() {
    const [openDialog, setOpenDialog] = React.useState(false);
    const handleClickOpen = () => {
        setOpenDialog(true);
    };

    const handleClose = () => {
        setOpenDialog(false);
    };
    return (
        <Card sx={{height: 100, width: '90%', marginTop: '10px'}}>
            <CardContent>
                <Typography sx={{fontSize: 14}} color="text.secondary" gutterBottom>

                </Typography>
                <Button onClick={handleClickOpen}>
                    Добавить ссылку на фейковую новость
                </Button>
            </CardContent>
            <Dialog open={openDialog} onClose={handleClose}>
                <DialogTitle>Добавить ссылку на фейковую новость</DialogTitle>
                <DialogContent>
                    <DialogContentText>

                    </DialogContentText>
                    <Box>
                        <TextField
                            autoFocus
                            label="Ссылка на новость"
                            type="text"
                            variant="standard"
                            fullWidth
                        />
                        <TextField
                            autoFocus
                            label="Ссылка на первоисточник"
                            type="text"
                            variant="standard"
                            fullWidth
                        />
                        <TextField
                            label="Комментарий"
                            type="text"
                            variant="standard"
                            multiline
                            minRows={3}
                            fullWidth
                        />
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose}>Закрыть</Button>
                    <Button onClick={handleClose}>Отправить</Button>
                </DialogActions>
            </Dialog>
        </Card>

    );
}

export default Index;
