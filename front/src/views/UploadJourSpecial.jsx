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

export default function Upload() {
    const [students, setStudents] = useState([]);
    const [selectedFile, setSelectedFile] = useState(null);
    const [openDialog, setOpenDialog] = useState(false);
    const [openSnackbar, setOpenSnackbar] = useState(false);
    const [snackbarMessage, setSnackbarMessage] = useState("");
    const [snackbarSeverity, setSnackbarSeverity] = useState("success");
    const [processed, setProcessed] = useState(false);
    const [failedProcessing, setFailedProcessing] = useState([]);
    const [createdProcessing, setCreatedProcessing] = useState([]);
    const [successProcessing, setSuccessProcessing] = useState(false);
    const [isAdmin, setIsAdmin] = useState(false);


    const handleFileChange = (event) => {
        const file = event.target.files[0];
        const fileType = file.type;
        const validFileTypes = ['text/csv'];
        setProcessed(false);
        setSuccessProcessing(false);

        if (validFileTypes.includes(fileType)) {
            setSelectedFile(file);
            setOpenSnackbar(true);
            setSnackbarMessage("Format du fichier valide");
            setSnackbarSeverity("success");

            // Fichier valide, continuer le traitement
        } else {
            // Fichier invalide, afficher un message d'erreur
            setOpenSnackbar(true);
            setSnackbarMessage("Le fichier doit être au format CSV.");
            setSnackbarSeverity("error");
        }
    };

    const handleCloseSnackbar = () => {
        setOpenSnackbar(false);
    };
    
    const sendFile = () => {
        const formData = new FormData();
        formData.append("csv_file", selectedFile);
        // On indique au backend de remplacer l'ancienne base
        formData.append("replace", "true");
    
        fetch("/api/upload/specialday", {
            method: "POST",
            credentials: "include",
            headers: {
                'X-CSRFToken': Cookies.get("csrftoken")
            },
            body: formData,
        })
            .then((res) => res.json())
            .then((result) => {
                setProcessed(true);
                setSelectedFile(null);
                if (result.success) {
                    setSuccessProcessing(true);
                    // On met à jour createdProcessing, que le tableau soit vide ou non
                    setCreatedProcessing(result.created);
                    if (result.failed.length > 0) {
                        setOpenSnackbar(true);
                        setSnackbarMessage("Import partiellement réussi : la base a été remplacée mais certains jours n'ont pas pu être importés.");
                        setSnackbarSeverity("warning");
                        setFailedProcessing(result.failed);
                    } else {
                        setOpenSnackbar(true);
                        setSnackbarMessage("Import et remplacement des journées pédagogiques réussi");
                        setSnackbarSeverity("success");
                        // Dans ce cas, result.created contient la liste des jours créés (peut être non vide)
                    }
                } else {
                    setSuccessProcessing(false);
                    setOpenSnackbar(true);
                    setSnackbarMessage("Erreur lors de l'import des journées pédagogiques");
                    setSnackbarSeverity("error");
                }
            });
    };
    
        
    const handleImportClick = () => {
        if (selectedFile) {
            setOpenSnackbar(true);
            setSnackbarMessage("Import des journées pédagogiques en cours...");
            setSnackbarSeverity("info");
            sendFile();
        }
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
        {isAdmin && (
            <>
            <TopBar title="Gestion My2A > Imports" />
            <Grid
            container
            style={{ marginTop: '30px', alignItems: "center", justifyContent: "center" }}
            >
            <Grid item md={6} rowGap={8} spacing={12}>
            <Box
            sx={{
                backgroundColor: "white",
                paddingBottom: 2,
                borderRadius: "0 0 16px 16px",
            }}
            >
            <SectionBar
            title="Importer des journées pédagogiques"
            infos={
                "Le fichier doit être au format CSV. La première ligne doit être la même que dans l'exemple à télécharger ci-dessous. Attention, le fichier doit comporter l'ensemble des journées pédagogiques puisqu'il supprimera les anciens jours."
            }
            showInfo={true}
            exampleFile="/exempleJourSpecial.csv"
            />
            {/* Les deux boutons pour importer */}
            <div style={{ marginBottom: 40 }}></div>
            <Grid container justifyContent="center" columnGap={4}>
            <Button
            component="label"
            variant="contained"
            disableElevation
            color="secondary"
            startIcon={<CloudUploadIcon />}
            disabled={selectedFile !== null}
            >
            {selectedFile ? selectedFile.name : "Sélectionner un fichier"}
            <VisuallyHiddenInput type="file" onChange={handleFileChange} />
            </Button>
            {selectedFile && (
                <IconButton
                color="error"
                onClick={() => setSelectedFile(null)}
                style={{ marginLeft: -30 }}
                >
                <DeleteIcon />
                </IconButton>
            )}
            <Button
            variant="contained"
            color="secondary"
            endIcon={<SendIcon />}
            disableElevation
            disabled={selectedFile === null}
            onClick={handleImportClick}
            >
            Importer
            </Button>
            </Grid>
            
            {/* Affichage du résultat de l'import */}
            {processed && (
                <>
                {(createdProcessing.length > 0 || failedProcessing.length > 0) ? (
                    <>
                    {createdProcessing.length > 0 && (
                        <>
                        <Typography
                        sx={{ mt: 6, ml: 8 }}
                        variant="h6"
                        component="div"
                        >
                        Les journées pédagogiques suivants ont été créés :
                        </Typography>
                        <List sx={{ ml: 12 }}>
                        {createdProcessing.map((name) => (
                            <ListItem key={name} sx={{ height: 20 }}>
                            <ListItemText
                            primary={
                                <>
                                - <strong>{name}</strong>
                                </>
                            }
                            />
                            </ListItem>
                        ))}
                        </List>
                        </>
                    )}
                    {failedProcessing.length > 0 && (
                        <>
                        <Typography
                        sx={{ mt: 2, ml: 8 }}
                        variant="h6"
                        component="div"
                        >
                        Les journées pédagogiques suivants n'ont pas été ajoutés :
                        </Typography>
                        <List sx={{ ml: 12 }}>
                        {failedProcessing.map(([name, err]) => (
                            <ListItem key={name} sx={{ height: 45 }}>
                            <ListItemText
                            primary={
                                <>
                                - <strong>{name}</strong> : <em>{err}</em>
                                </>
                            }
                            />
                            </ListItem>
                        ))}
                        </List>
                        </>
                    )}
                    {failedProcessing.length === 0 && createdProcessing.length > 0 && (
                        <Typography
                        sx={{ mt: 2, ml: 8 }}
                        variant="h6"
                        component="div"
                        >
                        Tous les journées pédagogiques ont bien été importés !
                        </Typography>
                    )}
                    </>
                ) : (
                    <Typography
                    sx={{ mt: 6, ml: 8 }}
                    variant="h6"
                    component="div"
                    >
                    Aucune journée pédagogique n'a été ajoutée.
                    </Typography>
                )}
                </>
            )}
            </Box>
            </Grid>
            <GridBreak />
            <Grid item md={6} xs={11} sm={11}>
            {/* Zone réservée pour d'autres composants */}
            </Grid>
            </Grid>
            <Snackbar open={openSnackbar} autoHideDuration={6000} onClose={handleCloseSnackbar}>
            <MuiAlert
            onClose={handleCloseSnackbar}
            sx={{ width: '100%' }}
            severity={snackbarSeverity}
            variant="standard"
            >
            {snackbarMessage}
            </MuiAlert>
            </Snackbar>
            </>
        )}
            </div>
        );
    }