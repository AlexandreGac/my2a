import React, { useEffect, useState, forwardRef, useMemo } from "react";
import {
    Button,
    Grid,
    Typography,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Box,
    setRef,
    Radio, RadioGroup, FormLabel
} from "@mui/material";
import TopBar from "../components/TopBar";
import CustomProgressBar from "../components/ProgressBar";
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import SendIcon from '@mui/icons-material/Send';
import Checkbox from '@mui/material/Checkbox';
import Select from '@mui/material/Select';
import Cookies from 'js-cookie';
import '../styles/styles.css'
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Slide from '@mui/material/Slide';
import CircularProgress from '@mui/material/CircularProgress';
import { ects_base, required_ects, required_mandatory_courses, total_required_ects } from "../utils/utils";
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import TextField from "@mui/material/TextField";
import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";
import "react-pdf/dist/esm/Page/TextLayer.css";
import { jsPDF } from "jspdf";


pdfjs.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.js`;


const Transition = forwardRef(function Transition(props, ref) {
    return <Slide direction="up" ref={ref} {...props} />;
});
export default function Dashboard() {

    const [progress, setProgress] = useState(0)
    const [opened, setOpened] = useState('')
    const [departments, setDepartments] = useState([])
    const [departement, setDepartement] = useState(-1)
    const [parcoursList, setParcoursList] = useState([])
    const [parcours, setParcours] = useState(-1)
    const [mandatoryCourses, setMandatoryCourses] = useState([])
    const [mandatoryChoices, setMandatoryChoices] = useState([])
    const [choosenMandatoryCourses, setChoosenMandatoryCourses] = useState([])
    const [electiveCourses, setElectiveCourses] = useState([])
    const [choosenElectiveCourses, setChoosenElectiveCourses] = useState([])
    const [compatibleCourses, setCompatibleCourses] = useState([])
    const [isLogged, setIsLogged] = useState(false)
    const [editable, setEditable] = useState(false)
    const [confirmationDialogState, setConfirmationDialogState] = useState(false)
    const [student, setStudent] = useState({})
    const [comment, setComment] = useState('')
    const [parameters, setParameters] = useState({})
    const [semester, setSemester] = useState(1)
    const [displayedPdf, setDisplayedPdf] = useState(null);
    const [isEnrolling, setIsEnrolling] = useState(false);

    const timetable = useMemo(() => (
        { url: "/api/student/current/timetable/" }
    ), [choosenElectiveCourses, choosenMandatoryCourses, parcours])

    const hasInvalidMandatoryCourses = () => {
        let count = 0;
        for (const course of mandatoryCourses) {
            if (choosenMandatoryCourses.includes(course.name)) {
                count += 1;
            }
        }
        return count < required_mandatory_courses;
    }

    const hasInvalidMandatoryChoices = () => {
        for (const courses of mandatoryChoices) {
            let count = 0;
            for (const course of courses) {
                if (choosenMandatoryCourses.includes(course.name)) {
                    count += 1;
                }
            }
            if (count !== 1) {
                return true;
            }
        }
        return false;
    }

    const handleChange = (panel) => {
        if (opened != panel) setOpened(panel)
    }

    const getParcoursItems = () => {
        return parcoursList.map((parcours) => {
            return (
                <MenuItem value={parcours.id}>{parcours.name}</MenuItem>
            )
        })
    }

    const getParcoursName = (id) => {
        const temp = parcoursList.filter((p) => p.id == id)
        if (temp.length == 1) return temp[0].name
        else return null
    }

    const isCourseCompitable = (courseName) => {
        for (const index in compatibleCourses) {
            if (compatibleCourses[index].name == courseName) {
                return true
            }
        }
        return false
    }

    const getDepartmentCode = (id) => {
        const temp = departments.filter((dep) => dep.id == id)
        if (temp.length == 1) return temp[0].code
        else return null
    }

    const getDepartmentEndComment = (id) => {
        const temp = departments.filter((dep) => dep.id == id)
        if (temp.length == 1) return temp[0].end_comment
        else return null
    }


    const getMandatoryChoices = () => {
        return mandatoryChoices.map((courses) => {
            if (!isNaN(courses[0].day)) {
                return (
                    <Box sx={{
                        marginTop: "20px",
                    }}>
                        <FormLabel>{"Semaine d'ouverture (Semaine " + courses[0].day + ") :"}</FormLabel>
                            {
                                courses.map((course) => {
                                    return (
                                        <Box sx={{
                                            display: "flex",
                                            alignItems: "center",
                                            width: "100%",
                                            minHeight: "40px",
                                        }}>
                                            <FormControlLabel
                                                control={<Checkbox
                                                    defaultChecked={choosenMandatoryCourses.includes(course.name)}
                                                    onClick={(e) => {
                                                        changeEnrollment(course.name, e.target.checked, 'mandatory');
                                                    }}
                                                />}
                                                disabled={isEnrolling || !editable || !isCourseCompitable(course.name) && !choosenMandatoryCourses.includes(course.name)}
                                                label={'[' + course.code.replaceAll(" ", "") + '] ' + course.name + ' (' + course.ects + ' ECTS)'}
                                                value={course.id}
                                                sx={{
                                                    flex: 1, // Le texte occupe tout l'espace disponible
                                                    whiteSpace: "nowrap",
                                                    overflow: "hidden",
                                                    textOverflow: "ellipsis",
                                                    minHeight: "40px",
                                                    display: "flex",
                                                    alignItems: "center",
                                                }}
                                            />
                                            <Button
                                            variant="outlined"
                                            size="small"
                                            sx={{
                                                minWidth: "70px",
                                                textAlign: "center",
                                            }}
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleDescClick(course.code);
                                            }}
                                            >
                                            Desc
                                            </Button>
                                        </Box>
                                    )
                                })
                            }
                 </Box>
                )
            }
            else {
                return (
                    <Box sx={{
                        marginTop: "20px",
                    }}>
                        <FormLabel>{"Créneau : " + courses[0].day + ", " + courses[0].start_time + " - " + courses[0].end_time}</FormLabel>
                            {
                                courses.map((course) => {
                                    return (
                                        <Box sx={{
                                            display: "flex",
                                            alignItems: "center",
                                            width: "100%",
                                            minHeight: "40px",
                                        }}>
                                            <FormControlLabel
                                                control={<Checkbox
                                                    defaultChecked={choosenMandatoryCourses.includes(course.name)}
                                                    onClick={(e) => {
                                                        changeEnrollment(course.name, e.target.checked, 'mandatory');
                                                    }}
                                                />}
                                                disabled={isEnrolling || !editable || !isCourseCompitable(course.name) && !choosenMandatoryCourses.includes(course.name)}
                                                label={'[' + course.code.replaceAll(" ", "") + '] ' + course.name + ' (' + course.ects + ' ECTS)'}
                                                value={course.id}
                                                sx={{
                                                    flex: 1, // Le texte occupe tout l'espace disponible
                                                    whiteSpace: "nowrap",
                                                    overflow: "hidden",
                                                    textOverflow: "ellipsis",
                                                    minHeight: "40px",
                                                    display: "flex",
                                                    alignItems: "center",
                                                }}
                                            />
                                            <Button
                                                variant="outlined"
                                                size="small"
                                                sx={{
                                                    minWidth: "70px",
                                                    textAlign: "center",
                                                }}
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleDescClick(course.code);
                                                }}
                                            >
                                                Desc
                                            </Button>
                                        </Box>
                                    )
                                })
                            }
                    </Box>
                )
            }
        })
    }


    const handleDescClick = (courseCode) => {
        const cleanedCode = courseCode.trim();

        fetch(`/data/data/${cleanedCode}.json`)
            .then((res) => {
                if (!res.ok) {
                    throw new Error(`HTTP error! status: ${res.status}`);
                }
                return res.json();
            })
            .then((data) => {
                const doc = new jsPDF();

                doc.setFont('times', 'bold');
                doc.setFontSize(16);
                doc.text(`Description du cours ${cleanedCode}`, 10, 20);

                doc.setFontSize(12);
                let yPosition = 30;
                Object.keys(data).forEach((key) => {
                    doc.setFont('times', 'bold');
                    const text = `${key} : `;
                    const lines = doc.splitTextToSize(text, 180);
                    doc.text(lines, 10, yPosition);
                    yPosition += 5;
                    doc.setFont('times', 'normal');
                    const text2 = `${data[key]}`;
                    const lines2 = doc.splitTextToSize(text2, 180);
                    doc.text(lines2, 10, yPosition);
                    yPosition += lines2.length * 6;


                    if (yPosition > 280) {
                        doc.addPage();
                        yPosition = 20;
                    }
                });

                const pdfBlob = doc.output("blob");
                const pdfUrl = URL.createObjectURL(pdfBlob);
                setDisplayedPdf(pdfUrl);
                setSemester(1);
            })
            .catch((error) => {
                console.error("Erreur lors du chargement du fichier JSON :", error);
                const doc = new jsPDF();
                doc.setFontSize(16);
                doc.text("Fichier de description non trouvé.", 10, 20);
                const pdfBlob = doc.output("blob");
                const pdfUrl = URL.createObjectURL(pdfBlob);
                setDisplayedPdf(pdfUrl);
            });
    };

    const getMandatoryCourses = () => {
        return mandatoryCourses.map((course) => (
            <Box
                key={course.code}
                sx={{
                    display: "flex",
                    alignItems: "center",
                    width: "100%",
                    minHeight: "40px",
                }}
            >
                {/* Checkbox alignée à gauche */}
                <Checkbox
                    defaultChecked={choosenMandatoryCourses.includes(course.name)}
                    onClick={(e) => {
                        changeEnrollment(course.name, e.target.checked, "mandatory");
                    }}
                    disabled={
                        isEnrolling ||
                        !editable ||
                        (!isCourseCompitable(course.name) && !choosenMandatoryCourses.includes(course.name))
                    }
                />

                {/* Texte du cours */}
                <Box
                    sx={{
                        flex: 1, // Le texte occupe tout l'espace disponible
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        minHeight: "40px",
                        display: "flex",
                        alignItems: "center",
                    }}
                >
                    <Typography>
                        {"[" + course.code.replaceAll(" ", "") + "] " + course.name + " (" + course.ects + " ECTS)"}
                    </Typography>
                </Box>

                {/* Bouton Desc parfaitement aligné à droite */}
                <Button
                    variant="outlined"
                    size="small"
                    sx={{
                        minWidth: "70px",
                        textAlign: "center",
                    }}
                    onClick={(e) => {
                        e.stopPropagation();
                        handleDescClick(course.code);
                    }}
                >
                    Desc
                </Button>
            </Box>
        ));
    };

    const getElectiveCourses = () => {
        return electiveCourses.map((course) => (
            <Box key={course.code} sx={{ display: "flex", alignItems: "center", width: "100%", minHeight: "40px" }}>
                {/* Checkbox à gauche */}
                <Checkbox
                    defaultChecked={choosenElectiveCourses.includes(course.name)}
                    onClick={(e) => {
                        changeEnrollment(course.name, e.target.checked, "elective");
                    }}
                    disabled={
                        isEnrolling ||
                        !editable ||
                        (!isCourseCompitable(course.name) && !choosenElectiveCourses.includes(course.name))
                    }
                />

                {/* Texte du cours */}
                <Box
                    sx={{
                        flex: 1, // Prend tout l'espace disponible
                        whiteSpace: "nowrap", // Empêche le retour à la ligne
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        minHeight: "40px",
                        display: "flex",
                        alignItems: "center",
                    }}
                >
                    <Typography>
                        {"[" + course.code + "] " + course.name + " (" + course.ects + " ECTS)"}
                    </Typography>
                </Box>

                {/* Bouton Desc aligné sur la même colonne */}
                <Button
                    variant="outlined"
                    size="small"
                    sx={{
                        minWidth: "70px", // Assure que tous les boutons ont la même largeur
                        textAlign: "center",
                    }}
                    onClick={(e) => {
                        e.stopPropagation();
                        handleDescClick(course.code);
                    }}
                >
                    Desc
                </Button>
            </Box>
        ));
    };




    const getDepartmentDescription = (code) => {
        const temp = departments.filter((dep) => dep.id == code)
        if (temp.length == 1) return temp[0].description
        else return null
    }

    const getParcoursDescription = (code) => {
        const temp = parcoursList.filter((p) => p.id == code)
        if (temp.length == 1) return temp[0].description
        else return null
    }

    const getListCoursesHint = (parcours) => {
        const temp = parcoursList.filter((p) => p.id == parcours)
        if (temp.length == 1) return temp[0].mandatory_text
        else return null
    }

    const getElectiveCoursesHint = (parcours) => {
        const temp = parcoursList.filter((p) => p.id == parcours)
        if (temp.length == 1) return temp[0].elective_text
        else return null
    }

    const changeParcours = (code) => {
        setParcours(code)
        fetch('/api/student/current/parcours/', {
            method: 'POST',
            credentials: "include",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify({ parcours: code }),
        })
            .then((res) => res.json())
            .then((result) => {
                setOpened('obligatoires')
                setProgress(67)
            },
                (error) => {
                    console.log(error)
                })
    }

    const changeEnrollment = (course, is_enrolled, category) => {
        setIsEnrolling(true);
        fetch('/api/student/current/enroll/', {
            method: 'POST',
            credentials: "include",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify({ course: course, is_enrolled: is_enrolled, category: category }),
        })
            .then((res) => { console.log(res); res.json();})
            .then((result) => {
                fetch('/api/student/current/courses/available', {
                    method: 'GET',
                    credentials: "include",
                    headers: {
                        'Content-Type': 'application/json',
                    },
                })
                    .then((res) => res.json())
                    .then((result_available) => {
                        fetch('/api/student/current/courses/available_electives', {
                            method: 'GET',
                            credentials: "include",
                            headers: {
                                'Content-Type': 'application/json',
                            },
                        })
                            .then((res) => res.json())
                            .then((result) => {
                                setElectiveCourses(result)
                                fetch('/api/student/current/id/', {
                                    method: 'GET',
                                    credentials: "include",
                                    headers: {
                                        'Content-Type': 'application/json',
                                    },
                                })
                                    .then((res) => res.json())
                                    .then((result) => {
                                        setStudent(result)
                                        const tempMandatory = []
                                        for (const index in result.mandatory_courses) {
                                            tempMandatory.push(result.mandatory_courses[index].course.name)
                                        }
                                        setChoosenMandatoryCourses(tempMandatory)
                                        const tempElective = []
                                        for (const index in result.elective_courses) {
                                            tempElective.push(result.elective_courses[index].course.name)
                                        }
                                        setChoosenElectiveCourses(tempElective)
                                        setCompatibleCourses(result_available)
                                    },
                                        (error) => {
                                            console.log(error);
                                        })
                            },
                                (error) => {
                                    console.log(error);
                                })
                    },
                        (error) => {
                            console.log(error);
                        })
            },
                (error) => {
                    console.log(error)
                })
        .catch((error) => {
            console.log(error);
        })
        .finally(() => {
            setTimeout(() => {
                setIsEnrolling(false);
            }, 1000);
        });
    }

    const validateForm = () => {
        fetch('/api/student/updatestatus/', {
            method: 'POST',
            credentials: "include",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify({ comment: comment }),
        })
            .then((res) => res.json)
            .then((result) => {
                setConfirmationDialogState(false)
                window.location.href = '/dashboard'
            })
    }

    useEffect(() => {
        fetch('/api/parameters', {
            method: 'GET',
            credentials: "include",
            headers: {
                'Content-Type': 'application/json',
            },
        })
            .then((res) => res.json())
            .then((result) => {
                const temp = {}
                for (const index in result) {
                    temp[result[index].name] = result[index].value
                }
                setParameters(temp)
            })
        fetch('/api/student/current/', {
            method: 'GET',
            credentials: "include",
            headers: {
                'Content-Type': 'application/json',
            },
        })
            .then((res) => res.json())
            .then((result) => {
                if (result.detail != null && result.detail == "Informations d'authentification non fournies.") {
                    window.location.href = '/accounts/login/'
                } else {
                    setIsLogged(true)
                    fetch('/api/department/', {
                        method: 'GET',
                        credentials: "include",
                        headers: {
                            'Content-Type': 'application/json',
                        },
                    })
                        .then((res) => res.json())
                        .then((result) => {
                            setDepartments(result)
                        },
                            (error) => {
                                console.log(error);
                            })

                    fetch('/api/student/current/id/', {
                        method: 'GET',
                        credentials: "include",
                        headers: {
                            'Content-Type': 'application/json',
                        },
                    })
                        .then((res) => res.json())
                        .then((result) => {
                            setStudent(result)
                            setEditable(result.editable)
                            if (result.department != null) {
                                setDepartement(result.department)
                                setOpened('parcours')
                                setProgress(34)
                            }

                            if (result.parcours != null) {
                                setParcours(result.parcours)
                                setOpened('obligatoires')
                                setProgress(67)
                            }

                            const tempMandatory = []
                            for (const index in result.mandatory_courses) {
                                tempMandatory.push(result.mandatory_courses[index].course.name)
                            }
                            setChoosenMandatoryCourses(tempMandatory)

                            const tempElective = []
                            for (const index in result.elective_courses) {
                                tempElective.push(result.elective_courses[index].course.name)
                            }
                            setChoosenElectiveCourses(tempElective)

                        },
                            (error) => {
                                console.log(error);
                            })
                }
            },
                (error) => {
                    console.log(error);
                })
    }, [])

    useEffect(() => {
        if (departement != -1) {
            fetch('/api/parcours/?department=' + departement, {
                method: 'GET',
                credentials: "include",
                headers: {
                    'Content-Type': 'application/json',
                },
            })
                .then((res) => res.json())
                .then((result) => {
                    setParcoursList(result)
                },
                    (error) => {
                        console.log(error);
                    })
        }
    }, [departement])

    useEffect(() => {
        if (parcours != -1) {
            fetch('/api/course/?parcours=' + parcours + '&on_list=true', {
                method: 'GET',
                credentials: "include",
                headers: {
                    'Content-Type': 'application/json',
                },
            })
                .then((res) => res.json())
                .then((result) => {
                    let choices = Array
                        .from(Map.groupBy(result, (course) => course.start_time + course.day).values())
                        .filter((courses) => courses.length > 1);
                    let flat_choices = choices.flat();
                    let mandatory = result.filter((course) => !flat_choices.includes(course));
                    setMandatoryChoices(choices);
                    setMandatoryCourses(mandatory);
                },
                    (error) => {
                        console.log(error);
                    })

            fetch('/api/student/current/courses/available', {
                method: 'GET',
                credentials: "include",
                headers: {
                    'Content-Type': 'application/json',
                },
            })
                .then((res) => res.json())
                .then((result_available) => {
                    fetch('/api/student/current/courses/available_electives', {
                        method: 'GET',
                        credentials: "include",
                        headers: {
                            'Content-Type': 'application/json',
                        },
                    })
                        .then((res) => res.json())
                        .then((result) => {
                            setElectiveCourses(result)
                            fetch('/api/student/current/id/', {
                                method: 'GET',
                                credentials: "include",
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                            })
                                .then((res) => res.json())
                                .then((result) => {
                                    setStudent(result)
                                    const tempMandatory = []
                                    for (const index in result.mandatory_courses) {
                                        tempMandatory.push(result.mandatory_courses[index].course.name)
                                    }
                                    setChoosenMandatoryCourses(tempMandatory)

                                    const tempElective = []
                                    for (const index in result.elective_courses) {
                                        tempElective.push(result.elective_courses[index].course.name)
                                    }
                                    setChoosenElectiveCourses(tempElective)
                                    setCompatibleCourses(result_available)
                                    setEditable(result.editable)
                                },
                                    (error) => {
                                        console.log(error);
                                    })
                        },
                            (error) => {
                                console.log(error);
                            })
                },
                    (error) => {
                        console.log(error);
                    })

        }
    }, [parcours]);

    useEffect(() => {
        fetch('/api/student/current/courses/available', {
            method: 'GET',
            credentials: "include",
            headers: {
                'Content-Type': 'application/json',
            },
        })
            .then((res) => res.json())
            .then((result) => {
                setCompatibleCourses(result)
                fetch('/api/student/current/courses/available_electives', {
                    method: 'GET',
                    credentials: "include",
                    headers: {
                        'Content-Type': 'application/json',
                    },
                })
                    .then((res) => res.json())
                    .then((result) => {
                        setElectiveCourses(result)
                    },
                        (error) => {
                            console.log(error);
                        })
            },
                (error) => {
                    console.log(error);
                })
    }, [parcours, choosenElectiveCourses, choosenMandatoryCourses])
    return (
        <>
            {isLogged && (
                <div>
                    <TopBar title="Mon parcours" />
                    <Grid container columnGap={10} style={{ marginTop: '30px', alignItems: "center", justifyContent: "center" }}>
                        <Grid item md={7} xs={11} sm={11}>
                            <CustomProgressBar progress={progress} />
                        </Grid>
                        {getDepartmentCode(departement) == 'GCC' && (
                            <Grid md={1}>
                                {/*<Typography sx={{ textAlign: "center", fontWeight: "bold" }}>ECTS</Typography>*/}
                                <Box sx={{ position: 'relative', display: 'inline-flex', marginBottom: 4 }}>
                                    <CircularProgress color={student.ects < required_ects ? "warning" : "success"} variant="determinate" value={student.ects > required_ects ? 100 : (student.ects) / required_ects * 100} size={120} thickness={3} />
                                    <Box sx={{
                                        top: 0,
                                        left: 0,
                                        bottom: 0,
                                        right: 0,
                                        width: 120,
                                        position: 'absolute',
                                        display: 'flex',
                                        alignItems: 'center',
                                        textAlign: 'center',
                                    }}>
                                        <Typography sx={{ fontWeight: 'bold', fontSize: 18 }} variant="caption" component="div">{student.ects} / {required_ects} ECTS </Typography>
                                    </Box>
                                </Box>
                            </Grid>
                        )}
                        {getDepartmentCode(departement) == 'IMI' && (
                            <Grid md={1}>
                                <Typography sx={{ textAlign: "center", fontWeight: "bold" }}>Total ECTS</Typography>
                                <Box sx={{ position: 'relative', display: 'inline-flex', marginBottom: 4 }}>
                                    <CircularProgress color={student.ects < total_required_ects ? "warning" : "success"} variant="determinate" value={student.ects > total_required_ects ? 100 : (student.ects) / total_required_ects * 100} size={120} thickness={3} />
                                    <Box sx={{
                                        top: 0,
                                        left: 0,
                                        bottom: 0,
                                        right: 0,
                                        width: 120,
                                        position: 'absolute',
                                        display: 'flex',
                                        alignItems: 'center',
                                        textAlign: 'center',
                                    }}>
                                        <Typography sx={{ fontWeight: 'bold', fontSize: 18 }} variant="caption" component="div">{student.ects} / {total_required_ects} ECTS </Typography>
                                    </Box>
                                </Box>
                            </Grid>
                        )}
                    </Grid>
                    <Grid container spacing={5} style={{ marginTop: '10px', justifyContent: "center" }}>
                        <Grid item xs={12}>
                            {getDepartmentDescription(departement) && (
                                <Box sx={{ textAlign: "center" }}>
                                    {
                                        getDepartmentDescription(departement).split("\r\n").map((part) => (
                                            <Typography sx={{ fontSize: "15px", marginBottom: "20px" }}>{part}</Typography>
                                        ))}
                                </Box>
                            )}
                        </Grid>
                        <Grid item md={5} xs={11} sm={11}>
                            <Accordion disabled={progress < 33} expanded={opened === 'parcours'} onChange={(e, expanded) => {
                                if (expanded) handleChange('parcours')
                            }}>
                                <AccordionSummary aria-controls="panel2d-content" id="panel2d-header" expandIcon={<ExpandMoreIcon />}>
                                    <Typography><b>Choix du parcours{parcours != -1 && ": " + getParcoursName(parcours)}</b></Typography>
                                </AccordionSummary>
                                <AccordionDetails>
                                    <FormControl fullWidth>
                                        <InputLabel>Parcours</InputLabel>
                                        <Select
                                            labelId="demo-simple-select-label"
                                            id="demo-simple-select"
                                            value={parcours}
                                            label="Parcours"
                                            onChange={(e) => {
                                                changeParcours(e.target.value)
                                            }}
                                            placeholder="Parcours"
                                            disabled={!editable}
                                        >
                                            {getParcoursItems()}
                                        </Select>
                                    </FormControl>
                                </AccordionDetails>
                            </Accordion>
                            {getParcoursDescription(parcours) && getParcoursDescription(parcours).split("\r\n").map((line) => (
                                <Typography sx={{ marginTop: "20px", marginLeft: "5px" }}>{line}</Typography>
                            ))}
                            <Box sx={{ marginTop: "20px" }} >
                                <Accordion disabled={progress < 66} expanded={opened === 'obligatoires'} onChange={(e, expanded) => {
                                    if (expanded) handleChange('obligatoires')
                                }}>
                                    <AccordionSummary aria-controls="panel3d-content" id="panel3d-header" expandIcon={<ExpandMoreIcon />}>
                                        <Typography><b>Choix des cours obligatoires sur liste</b></Typography>
                                    </AccordionSummary>
                                    <AccordionDetails>
                                        {getListCoursesHint(parcours) && getListCoursesHint(parcours).split("\r\n").map((part) => (
                                            <Typography sx={{ fontWeight: "bold", textDecoration: 'underline', fontSize: "15px", marginBottom: "10px" }}>{part}</Typography>
                                        ))}
                                        <FormGroup>
                                            {getMandatoryCourses()}
                                        </FormGroup>
                                    </AccordionDetails>
                                </Accordion>
                            </Box>
                            <Box sx={{marginTop: "20px"}} >
                                <Accordion disabled={progress < 66} expanded={opened === 'creneaux'} onChange={(e, expanded) => {
                                    if (expanded) handleChange('creneaux')
                                }}>
                                    <AccordionSummary aria-controls="panel3d-content" id="panel3d-header" expandIcon={<ExpandMoreIcon />}>
                                        <Typography><b>Choix des cours obligatoires sur créneau</b></Typography>
                                    </AccordionSummary>
                                    <AccordionDetails>
                                        <Typography sx={{ fontWeight: "bold", textDecoration: 'underline', fontSize: "15px", marginBottom: "10px" }}>Sélectionner un unique cours sur chacun des créneaux</Typography>
                                        {getMandatoryChoices()}
                                    </AccordionDetails>
                                </Accordion>
                            </Box>
                            <Box sx={{ marginBottom: "50px", marginTop: "20px" }} >
                                <Accordion disabled={progress < 66} expanded={opened === 'electifs'} onChange={(e, expanded) => {
                                    if (expanded) handleChange('electifs')
                                }}>
                                    <AccordionSummary aria-controls="panel3d-content" id="panel3d-header" expandIcon={<ExpandMoreIcon />}   >
                                        <Typography><b>Choix des cours électifs</b></Typography>
                                    </AccordionSummary>
                                    <AccordionDetails>
                                        {getElectiveCoursesHint(parcours) && getElectiveCoursesHint(parcours).split("\r\n").map((part) => (
                                            <Typography sx={{ fontWeight: "bold", textDecoration: 'underline', fontSize: "15px", marginBottom: "10px" }}>{part}</Typography>
                                        ))}
                                        <Box sx={{ height: "300px", overflowY: "scroll" }}>
                                            <FormGroup>
                                                {getElectiveCourses()}
                                            </FormGroup>
                                        </Box>
                                    </AccordionDetails>
                                </Accordion>
                            </Box>
                            {editable && (
                                <Button disabled={departement == -1 || parcours == -1} variant="contained" disableElevation style={{ marginTop: 10, float: "right", marginBottom: 20 }} onClick={() => {
                                    setConfirmationDialogState(true)
                                }} endIcon={<SendIcon />}>
                                    Confirmer
                                </Button>
                            )}
                        </Grid>
                        <Grid item md={6} xs={11} sm={11}>
                            <Box sx={{ marginBottom: "50px" }} >
                                <Button variant="contained" sx={{marginRight: "10px"}} onClick={() => {
                                    setDisplayedPdf(timetable);
                                    setSemester(1);
                                }}>
                                    Semestre 1
                                </Button>
                                <Button variant="contained" sx={{marginRight: "10px"}} onClick={() => {
                                    setDisplayedPdf(timetable);
                                    setSemester(2);
                                }}>
                                    Semestre 2
                                </Button>
                                <Button variant="contained" sx={{marginRight: "10px"}} onClick={() => {
                                    setDisplayedPdf(timetable);
                                    setSemester(3);
                                }}>
                                    Année Complète
                                </Button>
                                <Button variant="contained" sx={{marginRight: "10px"}} onClick={() => {
                                    window.open("/api/student/current/timetable/")
                                }}>
                                    Télécharger PDF
                                </Button>
                            </Box>
                            <Box sx={{ width: "100px" }}>
                                <Document
                                    file={(typeof displayedPdf === 'string' && displayedPdf.startsWith('blob:')) ? displayedPdf : timetable}
                                    onContextMenu={(e) => e.preventDefault()}
                                    className="pdf-container"
                                >
                                    {/* Si un PDF de description est affiché, on affiche sa première page ;
                                    sinon, on affiche le planning selon le semestre choisi */}
                                    <Page
                                        size="A2"
                                        pageNumber={semester}
                                        scale={1}
                                        renderTextLayer={false}
                                    />
                                </Document>
                            </Box>
                        </Grid>
                    </Grid>
                    <Dialog
                        open={confirmationDialogState}
                        TransitionComponent={Transition}
                        keepMounted
                        onClose={() => setConfirmationDialogState(false)}
                        aria-describedby="alert-dialog-slide-description"
                    >
                        <DialogTitle>{"Confirmer mes choix de cours ?"}</DialogTitle>
                        <DialogContent>
                            <DialogContentText id="alert-dialog-slide-description">
                                {getDepartmentEndComment(departement)}
                            </DialogContentText>
                            <DialogContentText sx={{ color: "red", fontWeight: "bold" }}>
                                {((getDepartmentCode(departement) === 'GCC' && student.ects < 48.5) || (getDepartmentCode(departement) === 'IMI' && student.ects < 60)) && "Attention: vous n'avez pas choisi suffisamment d'ECTS de cours."}
                            </DialogContentText>
                            <DialogContentText sx={{ color: "red", fontWeight: "bold" }}>
                                {hasInvalidMandatoryCourses() && "Vous devez choisir au moins 2 cours obligatoires sur liste."}
                            </DialogContentText>
                            <DialogContentText sx={{ color: "red", fontWeight: "bold" }}>
                                {hasInvalidMandatoryChoices() && "Attention: Vous devez sélectionner exactement un cours par créneau obligatoire."}
                            </DialogContentText>
                        </DialogContent>
                        <TextField sx={{ margin: 'auto', width: "90%" }} placeholder="Commentaire" value={comment} onChange={(e) => setComment(e.target.value)} />
                        <DialogActions>
                            <Button onClick={() => {
                                validateForm()
                            }}>Confirmer</Button>
                            <Button onClick={() => {
                                setConfirmationDialogState(false)
                            }}>Annuler</Button>
                        </DialogActions>
                    </Dialog>
                </div>
            )}
        </>
    )
}
