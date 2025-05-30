import { useEffect, useState, forwardRef } from 'react';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';

import TopBar from "../components/TopBar"
// import NavBar from "../components/NavBar"
import SectionBar from "../components/SectionBar";


import { Grid, MenuItem } from '@mui/material';
import IconButton from "@mui/material/IconButton";
import DownloadIcon from '@mui/icons-material/Download';
import EditIcon from "@mui/icons-material/Edit";
import RemoveRedEyeIcon from '@mui/icons-material/RemoveRedEye';
import MailOutlineIcon from '@mui/icons-material/MailOutline';
import { styled, alpha } from '@mui/material/styles';
import InputBase from '@mui/material/InputBase';
import SearchIcon from '@mui/icons-material/Search'
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Slide from '@mui/material/Slide';
import { required_ects } from "../utils/utils";
import Cookies from 'js-cookie';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';

const Transition = forwardRef(function Transition(props, ref) {
    return <Slide direction="up" ref={ref} {...props} />;
});

const GridBreak = styled('div')(({ theme }) => ({
    width: '100%',
}))

const Search = styled('div')(({ theme }) => ({
    position: 'relative',
    borderRadius: theme.shape.borderRadius,
    backgroundColor: alpha(theme.palette.common.white, 1),
    '&:hover': {
        backgroundColor: alpha(theme.palette.common.white, 0.25),
    },
    marginLeft: 0,
    width: '100%',
    marginBottom: 10

}));

const SearchIconWrapper = styled('div')(({ theme }) => ({
    padding: theme.spacing(0, 2),
    height: '100%',
    position: 'absolute',
    pointerEvents: 'none',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
}));

const StyledInputBase = styled(InputBase)(({ theme }) => ({
    color: 'inherit',
    width: '100%',
    '& .MuiInputBase-input': {
        padding: theme.spacing(1, 1, 1, 0),
        // vertical padding + font size from searchIcon
        paddingLeft: `calc(1em + ${theme.spacing(4)})`,
        transition: theme.transitions.create('width'),
        [theme.breakpoints.up('sm')]: {
            width: '12ch',
            '&:focus': {
                width: '20ch',
            },
        },
    },
}));

export default function Inspector() {

    const [students, setStudents] = useState([])
    const [search, setSearch] = useState('')
    const [open, setOpen] = useState(false);
    const [currentStudent, setCurrentStudent] = useState([])
    const [editOpened, setEditOpened] = useState(false)
    const [labels, setLabels] = useState({})
    const [isAdmin, setIsAdmin] = useState(false)
    const [departments, setDepartments] = useState([])
    const [currentDepartment, setCurrentDepartment] = useState(null)

    // State for the email sending status dialog
    const [emailStatusDialogOpen, setEmailStatusDialogOpen] = useState(false);
    const [emailStatusInfo, setEmailStatusInfo] = useState({ message: "", details: null });

    const handleClose = () => {
        setOpen(false);
    };

    const updateStudents = () => {
        fetch("/api/student/" + (currentDepartment != null ? "?department=" + currentDepartment : ""), {
            method: "GET",
            credentials: "include",
            headers: {
                'Content-Type': 'application/json',
            },
        })
            .then((res) => res.json())
            .then((result) => {
                setStudents(result)
            })
    }

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
                    updateStudents()
                    fetch("/api/labels/", {
                        method: "GET",
                        credentials: "include",
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    })
                        .then((res) => res.json())
                        .then((result) => {
                            setLabels(result)
                        })
                }
            })
            fetch("/api/department/", {
                method: "GET",
                credentials: "include",
                headers: {
                    'Content-Type': 'application/json'
                }
            })
                .then((res) => res.json())
                .then((result) => {
                    setDepartments(result)
                })
    }, [])

    const updateSearch = (search) => {
        fetch("/api/student/search?search=" + search + (currentDepartment != null ? "&department=" + currentDepartment : ""), {
            method: "GET",
            credentials: "include",
            headers: {
                'Content-Type': 'application/json',
            },
        })
            .then((res) => res.json())
            .then((result) => {
                setStudents(result)
            })
    }

    const fetchStudentData = (id) => {
        fetch("/api/student/" + id, {
            method: "GET",
            credentials: "include",
            headers: {
                'Content-Type': 'application/json',
            },
        })
            .then((res) => res.json())
            .then((result) => {
                setCurrentStudent(result)
                setOpen(true)
            })
    }

    const changeStudentStatus = (id) => {
        fetch("/api/student/updatestatus/", {
            method: "POST",
            credentials: "include",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify({ id: id })
        })
            .then((res) => res.json())
            .then((result) => {
                setEditOpened(false)
                updateStudents()
            })
    }

    useEffect(() => {
        updateStudents()
    }, [currentDepartment])


    useEffect(() => {
        updateSearch(search)
    }, [search])

    const getDepartmentItems = () => {
        return departments.map((department) => {
            return (
                <MenuItem value={department.id}>{department.code}</MenuItem>
            )
        })
    }

    const handleSendAccountCreationEmails = () => {
        setEmailStatusInfo({ message: "Envoi en cours...", details: null });
        setEmailStatusDialogOpen(true);

        fetch("/api/admin/send-bulk-account-creation-emails/", {
            method: "POST",
            credentials: "include",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
        })
        .then((res) => {
            if (!res.ok) {
                // Attempt to parse JSON error from backend
                return res.json().then(errorData => {
                    const backendError = errorData.detail || errorData.error || `Erreur ${res.status}`;
                    throw new Error(backendError);
                }).catch(() => {
                    // If parsing JSON fails, or res.json() itself fails
                    throw new Error(`Erreur ${res.status}: ${res.statusText}`);
                });
            }
            return res.json(); // If res.ok, parse the successful JSON response
        })
        .then((result) => {
            let statusMsg = result.message || "Opération terminée.";
            if (result.sent_count !== undefined) { // Check if sent_count exists
                statusMsg += ` ${result.sent_count} email(s) déclenché(s).`;
            }
            if (result.skipped_enpc_domain > 0) {
                statusMsg += ` ${result.skipped_enpc_domain} ignoré(s) (domaine @eleves.enpc.fr).`;
            }
            setEmailStatusInfo({ message: statusMsg, details: result });
        })
        .catch((error) => {
            console.error("Erreur lors de l'envoi des emails de création de compte:", error);
            setEmailStatusInfo({
                message: `Erreur: ${error.message || "Impossible d'envoyer les emails."}`,
                details: { errors: [{ error: error.message || "Erreur inconnue" }] } // Structure for error display
            });
        });
    };

    return (
        <div>

            {isAdmin && (
                <div>
                    <TopBar title="Gestion My2A" />

                    <Grid container style={{ marginTop: '30px', alignItems: "center", justifyContent: "center" }}>
                        <Grid item md={6}>
                            <FormControl sx={{marginBottom: 3}} fullWidth>
                                <InputLabel>Département</InputLabel>
                                <Select
                                    labelId="demo-simple-select-label"
                                    id="demo-simple-select"
                                    value={currentDepartment}
                                    label="Département"
                                    onChange={(e) => {
                                        setCurrentDepartment(e.target.value)
                                    }}
                                >
                                    {getDepartmentItems()}
                                </Select>
                            </FormControl>
                            <SectionBar title="Parcourir les étudiants" />
                            <div style={{ marginBottom: '10px' }}></div>
                            <Search>
                                <SearchIconWrapper>
                                    <SearchIcon />
                                </SearchIconWrapper>
                                <StyledInputBase
                                    placeholder="Search…"
                                    inputProps={{ 'aria-label': 'search' }}
                                    onChange={(event) => setSearch(event.target.value)}
                                />
                            </Search>
                        </Grid>
                        <GridBreak />

                        <Grid item md={6} xs={11} sm={11}>
                            <Button sx={{ marginBottom: 2, marginRight: 2}} variant="outlined" onClick={() => { window.location = "/api/students/export" + (currentDepartment !=  null ? "?dep=" + currentDepartment : "")}} startIcon={<DownloadIcon />} >Télécharger l'Excel</Button>
                            <Button sx={{ marginBottom: 2, marginRight: 2}} variant="outlined" onClick={() => { window.location = "/inspector/upload/student" }} startIcon={<DownloadIcon />} >Ajouter des élèves</Button>
                            <Button sx={{ marginBottom: 2, marginRight: 2}} variant="outlined" onClick={() => { window.location = "/inspector/upload/course" }} startIcon={<DownloadIcon />} >Ajouter des cours</Button>
                            <Button sx={{ marginBottom: 2, marginRight: 2}} variant="outlined" onClick={() => { window.location = "/inspector/upload/specialday" }} startIcon={<EditIcon />} >Modifier les jours spéciaux</Button>
                            <Button sx={{ marginBottom: 2, marginRight: 2}} variant="outlined" onClick={() => { window.location = "/inspector/yearinformations" }} startIcon={<EditIcon />} >Modifier les informations de l'année</Button>
                            <Button sx={{ marginBottom: 2, marginRight: 2}} variant="outlined" onClick={() => { window.location = "/inspector/parcours" }} startIcon={<RemoveRedEyeIcon />} >Modifier les parcours</Button>
                            <Button sx={{ marginBottom: 2, marginRight: 2}} variant="outlined" onClick={() => { window.location = "/inspector/courses" }} startIcon={<RemoveRedEyeIcon />} >Voir la liste des cours</Button>
                            <Button sx={{ marginBottom: 2, marginRight: 2}} variant="outlined" onClick={handleSendAccountCreationEmails} startIcon={<MailOutlineIcon />} >Envoyer Emails Création Compte</Button>
                            <List dense sx={{ bgcolor: 'background.paper' }}>
                                {students.map((value) => {
                                    const labelId = `checkbox-list-secondary-label-${value}`;
                                    return (
                                        <ListItem
                                            key={value.surname + value.name}
                                            disablePadding
                                            style={{ backgroundColor: value.editable ? (value.has_logged_in ? 'rgba(255, 120, 0, 0.47)' : 'rgba(255, 0, 0, 0.2)') : 'rgba(0, 255, 0, 0.2)' }}
                                            secondaryAction={
                                                <>
                                                    <IconButton edge="end" aria-label="removeredeye" onClick={() => {
                                                        fetchStudentData(value.id)
                                                    }}>
                                                        <RemoveRedEyeIcon />
                                                    </IconButton>
                                                    <IconButton aria-label="edit" style={{ marginLeft: '10px' }} onClick={
                                                        () => {
                                                            setCurrentStudent(value)
                                                            setEditOpened(true)
                                                        }
                                                    }>
                                                        <EditIcon />
                                                    </IconButton>
                                                </>
                                            }
                                        >
                                            {/* Rq : mettre dans l'ordre alphabétique */}
                                            <ListItemButton>
                                                <ListItemText id={labelId} primary={`${value.surname}` + ` ${value.name}`} />
                                            </ListItemButton>
                                        </ListItem>
                                    );
                                })}
                            </List>
                        </Grid>
                    </Grid>
                    <Dialog
                        open={open}
                        TransitionComponent={Transition}
                        keepMounted
                        onClose={handleClose}
                        aria-describedby="alert-dialog-slide-description"
                    >
                        <DialogTitle>{currentStudent.surname} {currentStudent.name}</DialogTitle>
                        <DialogContent>
                            <DialogContentText>
                                <DialogContentText>
                                    <strong>Département</strong> : {labels.departments && labels.departments[currentStudent.department?.toString()]}
                                </DialogContentText>
                            </DialogContentText>
                            <DialogContentText>
                                <strong>Parcours</strong> : {labels.parcours && labels.parcours[currentStudent.parcours?.toString()]}
                            </DialogContentText>
                            <DialogContentText>
                                <strong>ECTS</strong> : <span style={{ fontWeight: currentStudent.ects < required_ects ? 'bold' : 'normal', color: currentStudent.ects < required_ects ? 'red' : 'black' }}>{currentStudent.ects}</span>
                            </DialogContentText>
                            <DialogContentText id="alert-dialog-slide-description">
                                <strong>Cours obligatoires</strong>
                                <List dense sx={{ bgcolor: 'background.paper' }}>
                                    {currentStudent.mandatory_courses && currentStudent.mandatory_courses.map((value) => {
                                        const labelId = `checkbox-list-secondary-label-${value}`;
                                        return (
                                            <ListItem
                                                key={value.id}
                                                disablePadding
                                            >
                                                <ListItemText id={labelId} primary={`- ${value.course.name}`} />
                                            </ListItem>
                                        );
                                    })}
                                </List>
                                <strong>Courses électifs </strong>
                                <List dense sx={{ bgcolor: 'background.paper' }}>
                                    {currentStudent.elective_courses && currentStudent.elective_courses.map((value) => {
                                        const labelId = `checkbox-list-secondary-label-${value}`;
                                        return (
                                            <ListItem
                                                key={value.id}
                                                disablePadding
                                            >
                                                <ListItemText id={labelId} primary={`- ${value.course.name}`} />
                                            </ListItem>
                                        );
                                    })}
                                </List>
                            </DialogContentText>
                        </DialogContent>
                        <DialogActions>
                            <Button color="secondary" variant="outlined" onClick={() => { window.location = "/api/contract/" + currentStudent.id }} startIcon={<DownloadIcon />} >Imprimer</Button>
                            <Button color="inherit" variant="outlined" onClick={handleClose}>Fermer</Button>
                        </DialogActions>
                    </Dialog>
                    <Dialog
                        open={editOpened}
                        TransitionComponent={Transition}
                        keepMounted
                        onClose={() => { setEditOpened(false) }}
                        aria-describedby="alert-dialog-slide-description"
                    >
                        <DialogTitle>Rendre le profil de {currentStudent.name} {currentStudent.surname} modifiable ?</DialogTitle>
                        <DialogContent>
                            <DialogContentText id="alert-dialog-slide-description">
                                Attention: {currentStudent.name} pourra à nouveau modifier ses choix de cours.
                            </DialogContentText>
                        </DialogContent>
                        <DialogActions>
                            <Button onClick={() => { changeStudentStatus(currentStudent.id) }}>Confirmer</Button>
                            <Button onClick={() => { setEditOpened(false) }}>Annuler</Button>
                        </DialogActions>
                    </Dialog>

                    <Dialog
                        open={emailStatusDialogOpen}
                        onClose={() => setEmailStatusDialogOpen(false)}
                        aria-labelledby="email-status-dialog-title"
                        aria-describedby="email-status-dialog-description"
                    >
                        <DialogTitle id="email-status-dialog-title">Statut d'envoi des emails de création de compte</DialogTitle>
                        <DialogContent>
                            <DialogContentText id="email-status-dialog-main-message">
                                {emailStatusInfo.message}
                            </DialogContentText>
                            {emailStatusInfo.details && emailStatusInfo.details.errors && emailStatusInfo.details.errors.length > 0 && (
                                <>
                                    <DialogContentText sx={{ marginTop: 2, fontWeight: 'bold' }}>
                                        Erreurs détaillées:
                                    </DialogContentText>
                                    <List dense sx={{ maxHeight: 200, overflow: 'auto' }}>
                                        {emailStatusInfo.details.errors.map((error, index) => (
                                            <ListItem key={index}>
                                                <ListItemText
                                                    primary={error.student_name ? `Étudiant: ${error.student_name} (ID: ${error.student_id})` : `Étudiant ID: ${error.student_id || 'N/A'}`}
                                                    secondary={`Erreur: ${error.error}${error.user_email ? ' - Email: ' + error.user_email : ''}`}
                                                />
                                            </ListItem>
                                        ))}
                                    </List>
                                </>
                            )}
                        </DialogContent>
                        <DialogActions>
                            <Button onClick={() => setEmailStatusDialogOpen(false)}>Fermer</Button>
                        </DialogActions>
                    </Dialog>
                </div>
            )}
        </div>
    )
}
