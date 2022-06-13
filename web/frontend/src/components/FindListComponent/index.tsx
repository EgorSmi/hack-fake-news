import React from "react";
import {CheckResponse, FindItem} from "../../types/checkResponse";
import {
    Box,
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    TextField,
    Tooltip
} from "@mui/material";
import {CompareArrows, Link} from "@mui/icons-material";
import Typography from "@mui/material/Typography";

interface FindListInterface {
    items: FindItem[]
    result?: CheckResponse
    selectedItem: FindItem | undefined
    onSelectItem: (item: FindItem) => void
}

export const FindListComponent = (
    {items, result, onSelectItem, selectedItem}: FindListInterface): JSX.Element => {

    const [openDialog, setOpenDialog] = React.useState(false);
    const [rating, setRating] = React.useState(0);

    const handleClickOpen = (item: FindItem | undefined = undefined) => {
            setOpenDialog(true);
            if (item) {
                setRating(item?.rating || 0)
            }
        }
    ;

    const handleClose = () => {
        setOpenDialog(false);
    };

    const applyRating = () => {
        if (selectedItem) {
            if (rating < 0) {
                selectedItem.rating = 0;
            } else {
                if (rating > 100) {
                    selectedItem.rating = 100;
                } else {
                    selectedItem.rating = rating;
                }
            }

        }
        handleClose();
    };

    // const handleChange = (e:HTMLTextAreaElement) => {
    //     setRating(e.target.value);
    // };

    function renderItems() {
        return items.map((item, i) => {
            const selected = item === selectedItem
            return (
                <ListItem disablePadding key={i}>
                    {/*<ListItemButton onClick={() => {*/}
                    {/*    onSelectItem(item)*/}
                    {/*}}>*/}
                    <Tooltip title={'Соответствие источнику'}>
                        <Button variant="text" color="success">{item.score}%</Button>
                    </Tooltip>
                    <ListItemText
                        primary={item.name}
                        secondary={
                            <React.Fragment>
                                <Typography
                                    component="p"
                                    variant="body2"
                                    color="text.primary"
                                >
                                    Именованные сущности в источнике: <strong>{item.ner.join(',')}</strong>
                                </Typography>
                                <Typography
                                    component="p"
                                    variant="body2"
                                    color="text.primary"
                                >
                                    Именованные сущности в статье: <strong>{result?.ner.join(',') ?? ''}</strong>
                                </Typography>

                                <Typography
                                    component="p"
                                    variant="body2"
                                    color="text.primary"
                                >
                                    😁<strong>{Math.round((item.sentiment?.positive ?? 0) * 100)}</strong>%
                                    😐<strong>{Math.round((item.sentiment?.neutral ?? 0) * 100)}</strong>%
                                    😡<strong>{Math.round((item.sentiment?.negative ?? 0) * 100)}</strong>%
                                </Typography>
                                
                            </React.Fragment>
                        }/>
                    <Tooltip title={'Выделить похожий текст'}>
                        <ListItemIcon
                            style={{fill: selected ? '#b5f4b1' : undefined}}
                            onClick={() => {
                                onSelectItem(item)
                            }}>
                            <CompareArrows/>
                        </ListItemIcon>
                    </Tooltip>
                    <Tooltip title={'Перейти к оригинальной статье'}>
                        <ListItemIcon onClick={() => {
                            window.open(item.href, '_blank', 'noopener,noreferrer');
                        }}>
                            <Link/>
                        </ListItemIcon>
                    </Tooltip>
                    <Tooltip title={'Рейтинг статьи. Нажмите чтобы изменить'}>
                        <Button variant="text" onClick={() => handleClickOpen(item)}>{item.rating}%</Button>
                    </Tooltip>
                    {/*</ListItemButton>*/}
                </ListItem>
            )
        })
    }

    function renderDialog() {
        return (
            <Dialog open={openDialog} onClose={handleClose}>
                <DialogTitle>Изменить рейтинг статьи</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        Введите число от 0 до 100
                    </DialogContentText>
                    <TextField
                        autoFocus
                        margin="dense"
                        id="rating"
                        label="Рейтинг"
                        type="number"
                        variant="standard"
                        value={rating}

                        onChange={(e) => {
                            setRating(Number(e.target.value))
                        }}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose}>Закрыть</Button>
                    <Button onClick={applyRating}>Изменить</Button>
                </DialogActions>
            </Dialog>
        )
    }

    return (
        <Box sx={{marginTop: '10px'}}>
            <Typography variant="h6" color="text.secondary" sx={{textAlign: 'left'}} gutterBottom>
                Первоисточники
            </Typography>
            <List>
                {renderItems()}
            </List>
            {renderDialog()}
        </Box>
    )
}