// ===================================================================
// UTILITAIRES
// ===================================================================

/**
 * Récupère un cookie par son nom (pour le token CSRF Django)
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Formate un nombre avec séparateurs de milliers (ex: 1000000 → "1 000 000")
 */
function formaterMontant(nombre) {
    return Math.round(nombre).toLocaleString('fr-FR').replace(/,/g, ' ');
}

// ===================================================================
// GESTION DES POP-UPS
// ===================================================================

/**
 * Affiche le pop-up correspondant au type de caisse
 * @param {string} typeCaisse - 'Grande Caisse' ou 'Petite Caisse'
 */
function showPopup(typeCaisse) {
    let popupId, dateId;

    if (typeCaisse === 'Grande Caisse') {
        popupId = 'popup-container-gc';
        dateId = 'date-gc';
    } else if (typeCaisse === 'Petite Caisse') {
        popupId = 'popup-container-pc';
        dateId = 'date-pc';
    } else {
        return;
    }

    const popup = document.getElementById(popupId);
    if (popup) {
        popup.classList.remove('popup-hidden');
    }

    // Pré-remplir la date avec aujourd'hui
    const dateInput = document.getElementById(dateId);
    if (dateInput && !dateInput.value) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }
}

/**
 * Cache le pop-up et réinitialise le formulaire
 * @param {string} type - 'gc' ou 'pc'
 */
function hidePopup(type) {
    const container = document.getElementById('popup-container-' + type);
    const form = document.getElementById('form-' + type);

    if (container) {
        container.classList.add('popup-hidden');
    }
    if (form) {
        form.reset();
    }
}

// ===================================================================
// SOUMISSION DU FORMULAIRE (AJAX)
// ===================================================================

/**
 * Envoie le formulaire en AJAX et met à jour l'interface sans recharger
 * @param {string} type - 'gc' (Grande Caisse) ou 'pc' (Petite Caisse)
 */
function submitForm(type) {
    const form = document.getElementById('form-' + type);

    if (!form) {
        console.error('Formulaire introuvable : form-' + type);
        return;
    }

    // Validation basique côté client
    const montant = form.querySelector('[name="montant"]').value;
    const motif = form.querySelector('[name="motif"]').value.trim();
    const date = form.querySelector('[name="date"]').value;

    if (!montant || parseFloat(montant) <= 0) {
        alert('⚠️ Veuillez entrer un montant valide.');
        return;
    }
    if (!motif) {
        alert('⚠️ Veuillez entrer un motif.');
        return;
    }
    if (!date) {
        alert('⚠️ Veuillez entrer une date.');
        return;
    }

    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="button"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Envoi en cours...';

    fetch(AJOUTER_CAISSE_URL, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // ✅ Ajouter la ligne aux tableaux concernés
            ajouterLigneTableau(type, data.data);

            // ✅ Mettre à jour les totaux affichés
            if (data.totaux) {
                mettreAJourTotaux(data.totaux);
            }

            // ✅ Fermer le popup
            hidePopup(type);

            // ✅ Notification de succès
            afficherNotification('✅ Opération ajoutée avec succès !', 'success');
        } else {
            afficherNotification('❌ Erreur : ' + (data.error || 'Une erreur est survenue.'), 'error');
        }
    })
    .catch(error => {
        console.error('Erreur réseau :', error);
        afficherNotification('❌ Erreur réseau, veuillez réessayer.', 'error');
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    });
}

// ===================================================================
// MISE À JOUR DYNAMIQUE DES TABLEAUX ET TOTAUX
// ===================================================================

/**
 * Ajoute une nouvelle ligne au tableau spécifique + tableau récent
 * Utilise l'API DataTables pour rester compatible avec le tri/pagination
 */
function ajouterLigneTableau(type, data) {
    const typeCaisseComplet = type === 'gc' ? 'Grande Caisse' : 'Petite Caisse';
    const montantFormate = formaterMontant(data.somme) + ' ar';

    // 1. Tableau spécifique (Grande Caisse ou Petite Caisse)
    const tableSpecifiqueId = type === 'gc' ? 'table-grande-caisse' : 'table-petite-caisse';
    const tableSpecifique = document.getElementById(tableSpecifiqueId);

    if (tableSpecifique && $.fn.DataTable.isDataTable(tableSpecifique)) {
        $(tableSpecifique).DataTable().row.add([
            data.type_operation,
            data.date,
            data.motif,
            montantFormate
        ]).draw(false);
    }

    // 2. Tableau des opérations récentes (dashboard)
    const tableRecent = document.getElementById('table-recent');
    if (tableRecent && $.fn.DataTable.isDataTable(tableRecent)) {
        $(tableRecent).DataTable().row.add([
            typeCaisseComplet,
            data.type_operation,
            data.date,
            data.motif,
            montantFormate
        ]).draw(false);
    }
}

/**
 * Met à jour les totaux affichés (dashboard + résumé caisse)
 */
function mettreAJourTotaux(totaux) {
    const elementsToUpdate = [
        { id: 'total-caisse-affichage', valeur: totaux.total_caisse },
        { id: 'total-grande-caisse-affichage', valeur: totaux.total_grande_caisse },
        { id: 'total-petite-caisse-affichage', valeur: totaux.total_petite_caisse },
        { id: 'resume-grande-caisse', valeur: totaux.total_grande_caisse },
        { id: 'resume-petite-caisse', valeur: totaux.total_petite_caisse },
        { id: 'resume-total-caisse', valeur: totaux.total_caisse },
    ];

    elementsToUpdate.forEach(item => {
        const el = document.getElementById(item.id);
        if (el) {
            el.textContent = formaterMontant(item.valeur) + ' ar';
        }
    });
}

// ===================================================================
// NOTIFICATION DISCRÈTE (au lieu de alert)
// ===================================================================

/**
 * Affiche une notification en haut à droite
 * @param {string} message - Le message à afficher
 * @param {string} type - 'success' ou 'error'
 */
function afficherNotification(message, type = 'success') {
    let notif = document.getElementById('notification-popup');

    if (!notif) {
        notif = document.createElement('div');
        notif.id = 'notification-popup';
        notif.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 9999;
            font-family: Verdana, Geneva, Tahoma, sans-serif;
            font-size: 14px;
            font-weight: 600;
            color: white;
            transition: opacity 0.3s, transform 0.3s;
            opacity: 0;
            transform: translateX(100px);
            max-width: 350px;
        `;
        document.body.appendChild(notif);
    }

    // Couleur selon le type
    notif.style.background = type === 'error' ? '#ff7782' : '#41f1b6';
    notif.textContent = message;

    // Animer l'apparition
    setTimeout(() => {
        notif.style.opacity = '1';
        notif.style.transform = 'translateX(0)';
    }, 10);

    // Disparaître après 3 secondes
    clearTimeout(window._notifTimeout);
    window._notifTimeout = setTimeout(() => {
        notif.style.opacity = '0';
        notif.style.transform = 'translateX(100px)';
    }, 3000);
}