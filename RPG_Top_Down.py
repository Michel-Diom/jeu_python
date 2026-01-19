import pygame
import random
import sys

# Initialisation
pygame.init()

# Constantes
LARGEUR = 1000
HAUTEUR = 700
FPS = 60
TAILLE_TUILE = 50

# Couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
VERT = (34, 139, 34)
VERT_FONCE = (0, 100, 0)
BLEU = (70, 130, 180)
GRIS = (128, 128, 128)
GRIS_FONCE = (64, 64, 64)
MARRON = (139, 69, 19)
JAUNE = (255, 215, 0)
ROUGE = (220, 20, 60)
VIOLET = (138, 43, 226)
ORANGE = (255, 140, 0)

# Fenêtre
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("RPG Top-Down Adventure")
horloge = pygame.time.Clock()

class Joueur:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.largeur = 40
        self.hauteur = 40
        self.vitesse = 4
        self.direction = "bas"
        
        # Stats
        self.vie_max = 100
        self.vie = 100
        self.mana_max = 50
        self.mana = 50
        self.niveau = 1
        self.exp = 0
        self.exp_max = 100
        self.attaque = 15
        self.defense = 5
        self.or_total = 0
        
        # Inventaire
        self.inventaire = {
            "Potion de vie": 3,
            "Potion de mana": 2
        }
        
    def deplacer(self, dx, dy, obstacles):
        nouveau_x = self.x + dx
        nouveau_y = self.y + dy
        
        rect_joueur = pygame.Rect(nouveau_x, nouveau_y, self.largeur, self.hauteur)
        
        collision = False
        for obstacle in obstacles:
            if rect_joueur.colliderect(obstacle):
                collision = True
                break
        
        if not collision:
            self.x = nouveau_x
            self.y = nouveau_y
            
            if dx < 0:
                self.direction = "gauche"
            elif dx > 0:
                self.direction = "droite"
            elif dy < 0:
                self.direction = "haut"
            elif dy > 0:
                self.direction = "bas"
    
    def attaquer_ennemi(self, ennemi):
        degats = max(1, self.attaque - ennemi.defense)
        ennemi.vie -= degats
        return degats
    
    def utiliser_potion(self, type_potion):
        if type_potion in self.inventaire and self.inventaire[type_potion] > 0:
            if type_potion == "Potion de vie":
                self.vie = min(self.vie_max, self.vie + 50)
                self.inventaire[type_potion] -= 1
                return True
            elif type_potion == "Potion de mana":
                self.mana = min(self.mana_max, self.mana + 30)
                self.inventaire[type_potion] -= 1
                return True
        return False
    
    def gagner_exp(self, montant):
        self.exp += montant
        if self.exp >= self.exp_max:
            self.monter_niveau()
    
    def monter_niveau(self):
        self.niveau += 1
        self.exp = 0
        self.exp_max = int(self.exp_max * 1.5)
        self.vie_max += 20
        self.vie = self.vie_max
        self.mana_max += 10
        self.mana = self.mana_max
        self.attaque += 5
        self.defense += 2
    
    def dessiner(self, surface, camera_x, camera_y):
        x_ecran = self.x - camera_x
        y_ecran = self.y - camera_y
        
        # Corps
        pygame.draw.rect(surface, BLEU, (x_ecran, y_ecran, self.largeur, self.hauteur))
        
        # Tête
        pygame.draw.circle(surface, (255, 220, 177), 
                         (int(x_ecran + self.largeur // 2), int(y_ecran + 15)), 12)
        
        # Yeux
        if self.direction == "bas":
            pygame.draw.circle(surface, NOIR, (int(x_ecran + 15), int(y_ecran + 14)), 2)
            pygame.draw.circle(surface, NOIR, (int(x_ecran + 25), int(y_ecran + 14)), 2)
        elif self.direction == "haut":
            pygame.draw.circle(surface, NOIR, (int(x_ecran + 15), int(y_ecran + 16)), 2)
            pygame.draw.circle(surface, NOIR, (int(x_ecran + 25), int(y_ecran + 16)), 2)
        elif self.direction == "gauche":
            pygame.draw.circle(surface, NOIR, (int(x_ecran + 12), int(y_ecran + 15)), 2)
        else:
            pygame.draw.circle(surface, NOIR, (int(x_ecran + 28), int(y_ecran + 15)), 2)
        
        # Épée
        if self.direction == "droite":
            pygame.draw.line(surface, GRIS, (x_ecran + self.largeur, y_ecran + 20),
                           (x_ecran + self.largeur + 15, y_ecran + 20), 3)
        elif self.direction == "gauche":
            pygame.draw.line(surface, GRIS, (x_ecran, y_ecran + 20),
                           (x_ecran - 15, y_ecran + 20), 3)

class Ennemi:
    def __init__(self, x, y, type_ennemi="Slime"):
        self.x = x
        self.y = y
        self.largeur = 40
        self.hauteur = 40
        self.type = type_ennemi
        self.actif = True
        self.vitesse = 2
        
        if type_ennemi == "Slime":
            self.couleur = VERT
            self.vie_max = 30
            self.vie = 30
            self.attaque = 8
            self.defense = 2
            self.exp_donne = 20
            self.or_donne = 10
        elif type_ennemi == "Gobelin":
            self.couleur = (0, 150, 0)
            self.vie_max = 50
            self.vie = 50
            self.attaque = 12
            self.defense = 4
            self.exp_donne = 35
            self.or_donne = 20
        elif type_ennemi == "Boss":
            self.couleur = ROUGE
            self.vie_max = 150
            self.vie = 150
            self.attaque = 20
            self.defense = 8
            self.exp_donne = 100
            self.or_donne = 100
            self.largeur = 60
            self.hauteur = 60
    
    def deplacer_vers_joueur(self, joueur, obstacles):
        dx = joueur.x - self.x
        dy = joueur.y - self.y
        distance = (dx**2 + dy**2)**0.5
        
        if distance > 0 and distance < 200:
            dx = dx / distance * self.vitesse
            dy = dy / distance * self.vitesse
            
            nouveau_x = self.x + dx
            nouveau_y = self.y + dy
            
            rect_ennemi = pygame.Rect(nouveau_x, nouveau_y, self.largeur, self.hauteur)
            
            collision = False
            for obstacle in obstacles:
                if rect_ennemi.colliderect(obstacle):
                    collision = True
                    break
            
            if not collision:
                self.x = nouveau_x
                self.y = nouveau_y
    
    def attaquer_joueur(self, joueur):
        degats = max(1, self.attaque - joueur.defense)
        joueur.vie -= degats
        return degats
    
    def dessiner(self, surface, camera_x, camera_y):
        if self.actif:
            x_ecran = self.x - camera_x
            y_ecran = self.y - camera_y
            
            # Corps
            pygame.draw.ellipse(surface, self.couleur, 
                              (x_ecran, y_ecran, self.largeur, self.hauteur))
            
            # Yeux
            pygame.draw.circle(surface, NOIR, (int(x_ecran + 12), int(y_ecran + 15)), 3)
            pygame.draw.circle(surface, NOIR, (int(x_ecran + 28), int(y_ecran + 15)), 3)
            
            # Barre de vie
            barre_largeur = self.largeur
            barre_vie = int((self.vie / self.vie_max) * barre_largeur)
            pygame.draw.rect(surface, ROUGE, (x_ecran, y_ecran - 10, barre_largeur, 5))
            pygame.draw.rect(surface, VERT, (x_ecran, y_ecran - 10, barre_vie, 5))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.largeur, self.hauteur)

class PNJ:
    def __init__(self, x, y, nom, dialogues):
        self.x = x
        self.y = y
        self.largeur = 40
        self.hauteur = 40
        self.nom = nom
        self.dialogues = dialogues
        self.dialogue_actuel = 0
        
    def dessiner(self, surface, camera_x, camera_y):
        x_ecran = self.x - camera_x
        y_ecran = self.y - camera_y
        
        # Corps
        pygame.draw.rect(surface, VIOLET, (x_ecran, y_ecran, self.largeur, self.hauteur))
        
        # Tête
        pygame.draw.circle(surface, (255, 220, 177), 
                         (int(x_ecran + self.largeur // 2), int(y_ecran + 15)), 12)
        
        # Chapeau
        points = [
            (x_ecran + 20, y_ecran + 5),
            (x_ecran + 10, y_ecran + 5),
            (x_ecran + 20, y_ecran - 5)
        ]
        pygame.draw.polygon(surface, MARRON, points)
        
        # Nom
        font = pygame.font.Font(None, 20)
        texte = font.render(self.nom, True, BLANC)
        surface.blit(texte, (x_ecran - 10, y_ecran - 25))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.largeur, self.hauteur)
    
    def obtenir_dialogue(self):
        if self.dialogue_actuel < len(self.dialogues):
            dialogue = self.dialogues[self.dialogue_actuel]
            return dialogue
        return None

class Objet:
    def __init__(self, x, y, type_objet):
        self.x = x
        self.y = y
        self.type = type_objet
        self.ramasse = False
        self.taille = 30
        
        if type_objet == "coffre":
            self.couleur = JAUNE
            self.contenu = {"or": random.randint(20, 50)}
        elif type_objet == "potion_vie":
            self.couleur = ROUGE
            self.contenu = {"Potion de vie": 1}
        elif type_objet == "potion_mana":
            self.couleur = BLEU
            self.contenu = {"Potion de mana": 1}
    
    def dessiner(self, surface, camera_x, camera_y):
        if not self.ramasse:
            x_ecran = self.x - camera_x
            y_ecran = self.y - camera_y
            
            if self.type == "coffre":
                pygame.draw.rect(surface, self.couleur, 
                               (x_ecran, y_ecran, self.taille, self.taille))
                pygame.draw.rect(surface, NOIR, 
                               (x_ecran, y_ecran, self.taille, self.taille), 2)
            else:
                pygame.draw.circle(surface, self.couleur, 
                                 (int(x_ecran + self.taille // 2), 
                                  int(y_ecran + self.taille // 2)), 
                                 self.taille // 2)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.taille, self.taille)

def creer_monde():
    obstacles = []
    ennemis = []
    objets = []
    pnjs = []
    
    # Bordures
    obstacles.append(pygame.Rect(0, 0, 2000, 50))
    obstacles.append(pygame.Rect(0, 0, 50, 1500))
    obstacles.append(pygame.Rect(0, 1450, 2000, 50))
    obstacles.append(pygame.Rect(1950, 0, 50, 1500))
    
    # Arbres
    for i in range(30):
        x = random.randint(100, 1900)
        y = random.randint(100, 1400)
        obstacles.append(pygame.Rect(x, y, 60, 60))
    
    # Rochers
    for i in range(20):
        x = random.randint(100, 1900)
        y = random.randint(100, 1400)
        obstacles.append(pygame.Rect(x, y, 80, 50))
    
    # Maisons
    obstacles.append(pygame.Rect(300, 300, 100, 100))
    obstacles.append(pygame.Rect(500, 300, 100, 100))
    obstacles.append(pygame.Rect(400, 500, 100, 100))
    
    # Ennemis
    ennemis.append(Ennemi(800, 600, "Slime"))
    ennemis.append(Ennemi(900, 700, "Slime"))
    ennemis.append(Ennemi(1200, 800, "Gobelin"))
    ennemis.append(Ennemi(1300, 900, "Gobelin"))
    ennemis.append(Ennemi(1600, 1200, "Boss"))
    
    # PNJ
    dialogues_marchand = [
        "Bienvenue, aventurier!",
        "J'ai des potions à vendre.",
        "Reviens me voir!"
    ]
    pnjs.append(PNJ(350, 250, "Marchand", dialogues_marchand))
    
    dialogues_sage = [
        "Un terrible Boss terrorise la region...",
        "Elimine-le pour sauver notre village!",
        "Bonne chance, heros!"
    ]
    pnjs.append(PNJ(450, 250, "Sage", dialogues_sage))
    
    # Objets
    objets.append(Objet(600, 400, "coffre"))
    objets.append(Objet(1000, 600, "potion_vie"))
    objets.append(Objet(1100, 650, "potion_mana"))
    objets.append(Objet(1500, 1000, "coffre"))
    objets.append(Objet(700, 800, "potion_vie"))
    
    return obstacles, ennemis, pnjs, objets

def dessiner_monde(surface, obstacles, camera_x, camera_y):
    # Fond herbe
    for y in range(0, HAUTEUR, TAILLE_TUILE):
        for x in range(0, LARGEUR, TAILLE_TUILE):
            couleur = VERT if (x + y) % 100 == 0 else VERT_FONCE
            pygame.draw.rect(surface, couleur, (x, y, TAILLE_TUILE, TAILLE_TUILE))
    
    # Obstacles
    for obstacle in obstacles:
        x_ecran = obstacle.x - camera_x
        y_ecran = obstacle.y - camera_y
        
        if -100 < x_ecran < LARGEUR + 100 and -100 < y_ecran < HAUTEUR + 100:
            if obstacle.width == 60 and obstacle.height == 60:
                pygame.draw.rect(surface, MARRON, (x_ecran + 20, y_ecran + 30, 20, 30))
                pygame.draw.circle(surface, VERT_FONCE, 
                                 (int(x_ecran + 30), int(y_ecran + 20)), 25)
            elif obstacle.width == 80 and obstacle.height == 50:
                pygame.draw.ellipse(surface, GRIS, (x_ecran, y_ecran, 80, 50))
            elif obstacle.width == 100 and obstacle.height == 100:
                pygame.draw.rect(surface, MARRON, (x_ecran, y_ecran, 100, 100))
                pygame.draw.polygon(surface, ROUGE, [
                    (x_ecran, y_ecran),
                    (x_ecran + 50, y_ecran - 30),
                    (x_ecran + 100, y_ecran)
                ])
            else:
                pygame.draw.rect(surface, GRIS_FONCE, (x_ecran, y_ecran, 
                                                       obstacle.width, obstacle.height))

def dessiner_interface(surface, joueur):
    pygame.draw.rect(surface, GRIS_FONCE, (0, 0, LARGEUR, 100))
    pygame.draw.rect(surface, NOIR, (0, 0, LARGEUR, 100), 3)
    
    # Vie
    pygame.draw.rect(surface, NOIR, (20, 20, 204, 24), 2)
    barre_vie = int((joueur.vie / joueur.vie_max) * 200)
    pygame.draw.rect(surface, ROUGE, (22, 22, barre_vie, 20))
    
    # Mana
    pygame.draw.rect(surface, NOIR, (20, 50, 204, 24), 2)
    barre_mana = int((joueur.mana / joueur.mana_max) * 200)
    pygame.draw.rect(surface, BLEU, (22, 52, barre_mana, 20))
    
    # Textes
    font = pygame.font.Font(None, 24)
    
    texte_vie = font.render(f"Vie: {joueur.vie}/{joueur.vie_max}", True, BLANC)
    surface.blit(texte_vie, (230, 22))
    
    texte_mana = font.render(f"Mana: {joueur.mana}/{joueur.mana_max}", True, BLANC)
    surface.blit(texte_mana, (230, 52))
    
    texte_niveau = font.render(f"Niveau: {joueur.niveau}", True, JAUNE)
    surface.blit(texte_niveau, (450, 22))
    
    texte_exp = font.render(f"EXP: {joueur.exp}/{joueur.exp_max}", True, JAUNE)
    surface.blit(texte_exp, (450, 52))
    
    texte_or = font.render(f"Or: {joueur.or_total}", True, JAUNE)
    surface.blit(texte_or, (650, 37))
    
    # Inventaire
    font_petit = pygame.font.Font(None, 20)
    texte_inv = font_petit.render("Inventaire: [1] Vie x" + 
                                  str(joueur.inventaire.get("Potion de vie", 0)) +
                                  " [2] Mana x" + 
                                  str(joueur.inventaire.get("Potion de mana", 0)), 
                                  True, BLANC)
    surface.blit(texte_inv, (750, 37))

def afficher_dialogue(surface, pnj, dialogue):
    boite = pygame.Rect(50, HAUTEUR - 200, LARGEUR - 100, 150)
    pygame.draw.rect(surface, NOIR, boite)
    pygame.draw.rect(surface, BLANC, boite, 3)
    
    font_nom = pygame.font.Font(None, 28)
    texte_nom = font_nom.render(pnj.nom + ":", True, JAUNE)
    surface.blit(texte_nom, (70, HAUTEUR - 185))
    
    font_dialogue = pygame.font.Font(None, 24)
    lignes = []
    mots = dialogue.split()
    ligne_actuelle = ""
    
    for mot in mots:
        test_ligne = ligne_actuelle + mot + " "
        if font_dialogue.size(test_ligne)[0] < LARGEUR - 140:
            ligne_actuelle = test_ligne
        else:
            lignes.append(ligne_actuelle)
            ligne_actuelle = mot + " "
    lignes.append(ligne_actuelle)
    
    y_offset = 0
    for ligne in lignes[:3]:
        texte = font_dialogue.render(ligne, True, BLANC)
        surface.blit(texte, (70, HAUTEUR - 150 + y_offset))
        y_offset += 30
    
    font_petit = pygame.font.Font(None, 20)
    texte_continuer = font_petit.render("[E] Continuer", True, BLANC)
    surface.blit(texte_continuer, (LARGEUR - 200, HAUTEUR - 70))

def jeu():
    joueur = Joueur(100, 100)
    obstacles, ennemis, pnjs, objets = creer_monde()
    
    camera_x = 0
    camera_y = 0
    
    en_combat = False
    ennemi_combat = None
    cooldown_attaque = 0
    
    dialogue_actif = False
    pnj_dialogue = None
    
    messages = []
    temps_message = 0
    
    en_cours = True
    while en_cours:
        horloge.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                    if joueur.utiliser_potion("Potion de vie"):
                        messages.append("Potion de vie utilisee!")
                        temps_message = 120
                
                if event.key == pygame.K_2 or event.key == pygame.K_KP2:
                    if joueur.utiliser_potion("Potion de mana"):
                        messages.append("Potion de mana utilisee!")
                        temps_message = 120
                
                if event.key == pygame.K_e and dialogue_actif and pnj_dialogue:
                    pnj_dialogue.dialogue_actuel += 1
                    if pnj_dialogue.dialogue_actuel >= len(pnj_dialogue.dialogues):
                        dialogue_actif = False
                        pnj_dialogue.dialogue_actuel = 0
                
                if event.key == pygame.K_SPACE and en_combat and cooldown_attaque == 0:
                    degats = joueur.attaquer_ennemi(ennemi_combat)
                    messages.append(f"Vous infligez {degats} degats!")
                    temps_message = 60
                    cooldown_attaque = 30
                    
                    if ennemi_combat.vie <= 0:
                        ennemi_combat.actif = False
                        joueur.gagner_exp(ennemi_combat.exp_donne)
                        joueur.or_total += ennemi_combat.or_donne
                        messages.append(f"Victoire! +{ennemi_combat.exp_donne} EXP, +{ennemi_combat.or_donne} Or")
                        temps_message = 120
                        en_combat = False
                        ennemi_combat = None
        
        # Déplacement
        if not dialogue_actif and not en_combat:
            touches = pygame.key.get_pressed()
            dx = dy = 0
            
            if touches[pygame.K_LEFT] or touches[pygame.K_q]:
                dx = -joueur.vitesse
            if touches[pygame.K_RIGHT] or touches[pygame.K_d]:
                dx = joueur.vitesse
            if touches[pygame.K_UP] or touches[pygame.K_z]:
                dy = -joueur.vitesse
            if touches[pygame.K_DOWN] or touches[pygame.K_s]:
                dy = joueur.vitesse
            
            joueur.deplacer(dx, dy, obstacles)
        
        # Ennemis
        if not en_combat:
            for ennemi in ennemis:
                if ennemi.actif:
                    ennemi.deplacer_vers_joueur(joueur, obstacles)
        
        # Collision joueur-ennemi
        rect_joueur = pygame.Rect(joueur.x, joueur.y, joueur.largeur, joueur.hauteur)
        for ennemi in ennemis:
            if ennemi.actif and rect_joueur.colliderect(ennemi.get_rect()):
                en_combat = True
                ennemi_combat = ennemi
                break
        
        # Combat
        if en_combat and ennemi_combat and cooldown_attaque == 0:
            degats = ennemi_combat.attaquer_joueur(joueur)
            messages.append(f"{ennemi_combat.type} vous inflige {degats} degats!")
            temps_message = 60
            cooldown_attaque = 30
            
            if joueur.vie <= 0:
                return False
        
        if cooldown_attaque > 0:
            cooldown_attaque -= 1
        
        # PNJ
        for pnj in pnjs:
            if rect_joueur.colliderect(pnj.get_rect()):
                touches = pygame.key.get_pressed()
                if touches[pygame.K_e] and not dialogue_actif:
                    dialogue_actif = True
                    pnj_dialogue = pnj
        
        # Objets
        for objet in objets:
            if not objet.ramasse and rect_joueur.colliderect(objet.get_rect()):
                objet.ramasse = True
                for cle, valeur in objet.contenu.items():
                    if cle == "or":
                        joueur.or_total += valeur
                        messages.append(f"+{valeur} Or!")
                    else:
                        if cle in joueur.inventaire:
                            joueur.inventaire[cle] += valeur
                        else:
                            joueur.inventaire[cle] = valeur
                        messages.append(f"+{valeur} {cle}!")
                temps_message = 90
        
        # Caméra
        camera_x = joueur.x - LARGEUR // 2 + joueur.largeur // 2
        camera_y = joueur.y - HAUTEUR // 2 + joueur.hauteur // 2
        
        # Dessiner
        dessiner_monde(ecran, obstacles, camera_x, camera_y)
        
        for objet in objets:
            objet.dessiner(ecran, camera_x, camera_y)
        
        for pnj in pnjs:
            pnj.dessiner(ecran, camera_x, camera_y)
        
        for ennemi in ennemis:
            ennemi.dessiner(ecran, camera_x, camera_y)
        
        joueur.dessiner(ecran, camera_x, camera_y)
        
        dessiner_interface(ecran, joueur)
        
        # Messages
        if temps_message > 0:
            temps_message -= 1
            font = pygame.font.Font(None, 30)
            for i, msg in enumerate(messages[-3:]):
                texte = font.render(msg, True, JAUNE)
                ecran.blit(texte, (LARGEUR // 2 - texte.get_width() // 2, 120 + i * 35))
        
        # Dialogue
        if dialogue_actif and pnj_dialogue:
            dialogue = pnj_dialogue.obtenir_dialogue()
            if dialogue:
                afficher_dialogue(ecran, pnj_dialogue, dialogue)
        
        # Combat
        if en_combat:
            font = pygame.font.Font(None, 40)
            texte = font.render(f"Combat contre {ennemi_combat.type}! [ESPACE] Attaquer", True, ROUGE)
            ecran.blit(texte, (LARGEUR // 2 - texte.get_width() // 2, 120))
        
        # Victoire
        if all(not e.actif for e in ennemis if e.type == "Boss"):
            font = pygame.font.Font(None, 60)
            texte = font.render("VICTOIRE! Boss vaincu!", True, JAUNE)
            ecran.blit(texte, (LARGEUR // 2 - texte.get_width() // 2, HAUTEUR // 2))
        
        pygame.display.flip()
    
    return False

def main():
    # Écran de début
    ecran.fill(NOIR)
    
    font_titre = pygame.font.Font(None, 80)
    texte_titre = font_titre.render("RPG TOP-DOWN", True, JAUNE)
    ecran.blit(texte_titre, (LARGEUR // 2 - texte_titre.get_width() // 2, 150))
    
    font = pygame.font.Font(None, 35)
    instructions = [
        "CONTROLES:",
        "ZQSD ou Fleches - Se deplacer",
        "E - Interagir avec PNJ",
        "ESPACE - Attaquer en combat",
        "1 - Utiliser potion de vie",
        "2 - Utiliser potion de mana",
        "ESC - Quitter",
        "",
        "OBJECTIF:",
        "Explorez le monde, combattez les ennemis,",
        "parlez aux PNJ et vainquez le Boss!",
        "",
        "Cliquez pour commencer"
    ]
    
    y_offset = 250
    for instruction in instructions:
        if instruction == "CONTROLES:" or instruction == "OBJECTIF:":
            texte = font.render(instruction, True, ORANGE)
        else:
            texte = font.render(instruction, True, BLANC)
        ecran.blit(texte, (LARGEUR // 2 - texte.get_width() // 2, y_offset))
        y_offset += 35
    
    pygame.display.flip()
    
    attente = True
    while attente:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                attente = False
    
    # Lancer le jeu
    continuer = jeu()
    
    # Écran de fin
    if not continuer:
        ecran.fill(NOIR)
        font_fin = pygame.font.Font(None, 70)
        texte_fin = font_fin.render("GAME OVER", True, ROUGE)
        ecran.blit(texte_fin, (LARGEUR // 2 - texte_fin.get_width() // 2, HAUTEUR // 2 - 50))
        
        font_merci = pygame.font.Font(None, 40)
        texte_merci = font_merci.render("Merci d'avoir joue!", True, BLANC)
        ecran.blit(texte_merci, (LARGEUR // 2 - texte_merci.get_width() // 2, HAUTEUR // 2 + 50))
        
        pygame.display.flip()
        pygame.time.wait(3000)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()