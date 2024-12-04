# **VIS_2024**

Willkommen im **VIS_2024**-Repository! Dieses Repository dient als zentrale Anlaufstelle für alle Studierenden des Kurses **VIS3 (UE+VO)**. Hier finden Sie Inhalte, Vorlagen und Aufgaben.

---

## **Hinweise zur Nutzung**

- **Individuelle Repositories:** Bitte erstellen Sie einen **Fork** dieses Repositories für Ihre Arbeiten.
- **Keine direkten Commits auf den `master` Branch:** 
  - Jede*r Studierende bearbeitet die von mir gestellten Aufgaben in einem eigenen Branch.

### **Arbeitsablauf**

1. **Erstellen eines neuen Branches:**
   - Verwenden Sie einen aussagekräftigen Namen (z. B. `ihr_name/feature_name`):
     ```bash
     git checkout -b ihr_name/feature_name
     ```

2. **Arbeiten im eigenen Branch:**
   - Führen Sie Änderungen lokal durch und pushen Sie regelmäßig:
     ```bash
     git push origin ihr_name/feature_name
     ```

3. **Kein direkter Zugriff auf den `master` Branch:**
   - Der `master` Branch ist ausschließlich für allgemeine Vorlagen und Inhalte reserviert.

4. **Abruf von Updates:**
   - Neue Aufgaben und Änderungen werden im Upstream-Repository (dieses Repository) bereitgestellt. Laden Sie diese wie folgt in den **main-Branch Ihres eigenen Forks**:
     ```bash
     git fetch upstream
     git checkout main
     git merge upstream/main
     ```
   - **Hinweis:** Führen Sie den Merge nur in Ihrem eigenen `main` Branch durch, um Änderungen sauber zu integrieren und Konflikte zu minimieren.

5. **Abgabe von Aufgaben:**
   - Reichen Sie Ihre Arbeiten per **Pull-Request** an das Upstream-Repository (dieses Repository) ein.

---

## **Einreichung von Arbeiten**

- Alle Informationen zur Einreichung Ihrer Aufgaben finden Sie in den jeweiligen Unterordnern für Aufgaben. 
- Die Aufgaben sind als Markdown-Dateien bereitgestellt.

---
