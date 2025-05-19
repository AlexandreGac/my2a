import React from "react";
import '../styles/styles.css'

import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import InfoIcon from '@mui/icons-material/Info';
import DownloadIcon from '@mui/icons-material/Download';
import { styled, alpha } from '@mui/material/styles';
import { Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions, Button } from '@mui/material';

export default function SectionBar({ 
    title,
    infos,
    color,
    showInfo,
    exampleFile,
    showExampleButton = true // Set default value to true
}) {
    const [openDialog, setOpenDialog] = React.useState(false);

    const handleOpenDialog = () => {
        setOpenDialog(true);
    };

    const handleCloseDialog = () => {
        setOpenDialog(false);
    };

    const handleDownload = () => {
        const link = document.createElement('a');
        link.href = exampleFile;
        link.download = 'exemple.csv';
        link.click();
    };

    return (
        <AppBar position="static" color={color} elevation={0}>
            <Toolbar variant="dense">
                <Typography variant="h6" color="inherit" component="div" sx={{ flexGrow: 1 }}>
                    {title}
                </Typography>
                {showInfo && (
                    <div>
                        <IconButton size="large"
                            aria-label="account of current user"
                            aria-controls="menu-appbar"
                            aria-haspopup="true"
                            onClick={handleOpenDialog}
                            color="inherit">
                            <InfoIcon />
                        </IconButton>
                        <Dialog open={openDialog} onClose={handleCloseDialog}>
                            <DialogTitle>Explications</DialogTitle>
                            <DialogContent>
                                <DialogContentText>
                                    {infos}
                                </DialogContentText>
                            </DialogContent>
                            <DialogActions>
                                {showExampleButton && (
                                    <Button color="secondary" variant="outlined" onClick={handleDownload} startIcon={<DownloadIcon />}>Exemple.csv</Button>
                                )}
                                <Button color="inherit" variant="outlined" onClick={handleCloseDialog}>Fermer</Button>
                            </DialogActions>
                        </Dialog>
                    </div>
                )}
            </Toolbar>
        </AppBar>
    )
}
