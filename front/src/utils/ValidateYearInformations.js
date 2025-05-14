import dayjs from 'dayjs';

// Fonction qui vérifie si une date est un lundi
const isMonday = (date) => dayjs(date).day() === 1;

// Fonction qui vérifie si une date est un jeudi
const isThursday = (date) => dayjs(date).day() === 4;

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



/**
* Fonction vérifiant la validité des dates de l'année scolaire
* @param {Object} yearInfo - Objet contenant les dates de l'année scolaire
* @returns {Array} - Liste des erreurs détectées (tableau vide si aucune erreur)
*/
export const validateYearInfo = (yearInfo) => {
    const errors = [];
    
    const startYear = yearInfo.start_of_the_school_year;
    const endYear = yearInfo.end_of_school_year;
    
    if (!startYear || !endYear) {
        errors.push("Les dates de début et de fin d'année doivent être renseignées.");
        return errors; // Impossible de valider sans ces dates
    }
    
    Object.keys(yearInfo).forEach((key) => {
        const date = yearInfo[key];
        if (!date) return; // Ignore les valeurs vides
        
        if (key !== "start_of_the_school_year" && key !== "end_of_school_year") {
            if (dayjs(date).isBefore(dayjs(startYear))) {
                errors.push(`La date "${translations[key]}" (${date}) est avant le début de l'année scolaire (${startYear}).`);
            }
            if (dayjs(date).isAfter(dayjs(endYear))) {
                errors.push(`La date "${translations[key]}" (${date}) est après la fin de l'année scolaire (${endYear}).`);
            }
        }
        
        // Vérification des jours spécifiques
        if (key.startsWith("monday_of_") && !isMonday(date)) {
            errors.push(`La date "${translations[key]}" (${date}) doit être un lundi.`);
        }
        
        if (key === "easter_monday" && !isMonday(date)) {
            errors.push(`La date "${translations[key]}" (${date}) doit être un lundi.`);
        }
        
        if (key === "ascension_day" && !isThursday(date)) {
            errors.push(`La date "${translations[key]}" (${date}) doit être un jeudi.`);
        }
        
        if (key === "whit_monday" && !isMonday(date)) {
            errors.push(`La date "${translations[key]}" (${date}) doit être un lundi.`);
        }
    });
    
    return errors;
};
