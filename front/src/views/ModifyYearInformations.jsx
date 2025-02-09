import { useEffect, useState, forwardRef } from 'react';

import TopBar from "../components/TopBar"
import NavBar from "../components/NavBar"
import SectionBar from "../components/SectionBar";
// import MySnackBar from '../components/SnackBar';

import InfoIcon from '@mui/icons-material/Info';
import { styled, alpha } from '@mui/material/styles';
import { IconButton } from '@mui/material';
import ClearIcon from '@mui/icons-material/Clear';
import DeleteIcon from '@mui/icons-material/Delete';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import SendIcon from '@mui/icons-material/Send';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Slide from '@mui/material/Slide';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { List, ListItem, ListItemText } from '@mui/material';
import FolderIcon from '@mui/icons-material/Folder';
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord';
import ListItemIcon from '@mui/material/ListItemIcon';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Cookies from 'js-cookie';
import TextField from '@mui/material/TextField';

const GridBreak = styled('div')(({ theme }) => ({
    width: '100%',
}))

const VisuallyHiddenInput = styled('input')({
    clip: 'rect(0 0 0 0)',
    clipPath: 'inset(50%)',
    height: 1,
    overflow: 'hidden',
    position: 'absolute',
    bottom: 0,
    left: 0,
    whiteSpace: 'nowrap',
    width: 1,
});

export default function ModifyYearInformations() {
    const [yearInfo, setYearInfo] = useState({
        start_of_the_school_year: '',
        start_of_S3B: '',
        start_of_S4A: '',
        start_of_S4B: '',
        end_of_school_year: '',
        monday_of_autumn_holiday: '',
        monday_of_xmas_holiday: '',
        monday_of_winter_holiday: '',
        monday_of_spring_holiday: '',
        easter_monday: '',
        ascension_day: '',  
        whit_monday: '',    
    });
    const [openSnackbar, setOpenSnackbar] = useState(false);
    const [snackbarMessage, setSnackbarMessage] = useState("");
    const [snackbarSeverity, setSnackbarSeverity] = useState("success");
    const [isAdmin, setIsAdmin] = useState(false);


    /*     Dictionnaire utile pour traduire les clés des informations de l'année qui sont en anglais*/    
    const translations = {
        start_of_the_school_year: "Début de l'année scolaire",
        start_of_S3B: "Début de S3B",
        start_of_S4A: "Début de S4A",
        start_of_S4B: "Début de S4B",
        end_of_school_year: "Fin de l'année scolaire",
        monday_of_autumn_holiday: "Lundi des vacances d'automne",
        monday_of_xmas_holiday: "Lundi des vacances de Noël",
        monday_of_winter_holiday: "Lundi des vacances d'hiver",
        monday_of_spring_holiday: "Lundi des vacances de printemps",
        easter_monday : "Lundi de Pâques",
        ascension_day : "Jeudi de l'Ascension",
        whit_monday : "Lundi de Pentecôte",
    };

    useEffect(() => {
        fetch("/api/yearinformations", {
            method: "GET",
            credentials: "include",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get("csrftoken")
            },
        })
            .then((res) => res.json())
            .then((data) => {
                setYearInfo(data);
            })
            .catch((error) => {
                setOpenSnackbar(true);
                setSnackbarMessage("Erreur lors de la récupération des informations de l'année.");
                setSnackbarSeverity("error");
            });
    }, []);

    const handleChange = (event) => {
        const { name, value } = event.target;
        setYearInfo({
            ...yearInfo,
            [name]: value,
        });
    };

    const handleSubmit = () => {
        fetch("/api/yearinformations", {
            method: "POST",
            credentials: "include",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get("csrftoken")
            },
            body: JSON.stringify(yearInfo),
        })
            .then((res) => res.json())
            .then((data) => {
                setOpenSnackbar(true);
                setSnackbarMessage("Informations de l'année mises à jour avec succès.");
                setSnackbarSeverity("success");
            })
            .catch((error) => {
                setOpenSnackbar(true);
                setSnackbarMessage("Erreur lors de la mise à jour des informations de l'année.");
                setSnackbarSeverity("error");
            });
    };

    const handleCloseSnackbar = () => {
        setOpenSnackbar(false);
    };
    

    useEffect(() => {
        fetch("/api/student/current", {
            method: "GET",
            credentials: "include",
            headers: {
                'Content-Type': 'application/json',
            },
        })
            .then((res) => res.json())
            .then((result) => {
                if (result.is_admin === false) {
                    window.location = "/"
                } else {
                    setIsAdmin(true)
                }
            })

    }, []);

    return (
        <div>
            {isAdmin && <>
                <TopBar title="Gestion My2A > Informations de l'année" />
                <Grid container style={{ marginTop: '30px', alignItems: "center", justifyContent: "center" }}>
                    <Grid item md={6} rowGap={8} spacing={12}>
                        <Box sx={{ backgroundColor: "white", paddingBottom: 2, borderRadius: "0 0 16px 16px" }}>
                            <SectionBar
                                title="Modifier les informations de l'année"
                                infos={"Modifiez les dates des événements de l'année scolaire."}
                                showInfo={true}
                            />
                            <div style={{ marginBottom: 40 }}></div>
                            <Grid container justifyContent="center" columnGap={4} rowGap={3}>
                                {Object.keys(yearInfo).map((key) => (
                                    <Grid item xs={12} key={key}>
                                        <TextField
                                            fullWidth
                                            label={translations[key] || key.replace(/_/g, ' ')}
                                            name={key}
                                            value={yearInfo[key]}
                                            onChange={handleChange}
                                            type="date"
                                            InputLabelProps={{
                                                shrink: true,
                                            }}
                                        />
                                    </Grid>
                                ))}
                                <Grid item xs={12}>
                                    <Button variant="contained" color="secondary" endIcon={<SendIcon />} disableElevation onClick={handleSubmit}>
                                        Mettre à jour
                                    </Button>
                                </Grid>
                            </Grid>
                        </Box>
                    </Grid>
                    <GridBreak />
                    <Grid item md={6} xs={11} sm={11}>
                    </Grid>
                </Grid>
                <Snackbar open={openSnackbar} autoHideDuration={6000} onClose={handleCloseSnackbar}>
                    <MuiAlert onClose={handleCloseSnackbar} sx={{ width: '100%' }} severity={snackbarSeverity} variant="standard">
                        {snackbarMessage}
                    </MuiAlert>
                </Snackbar>
            </>}
        </div>
    )
}
