;;; export.el --- export org to html

;; Copyright (C) 2021 by rgb-24bit

;; Usage: emacs --srcipt export.el [all]

;;; Code:

(require 'org)

(defvar export-file-list '())
(defvar export-base-dirs `(,(expand-file-name ".")))


(defun export-get-changed-org-file ()
  (let ((status (shell-command-to-string "git status"))
        (pattern "\\b[0-9/-a-z.]+\\.org\\b") (start 0))
    (while (string-match-p pattern status start)
      (add-to-list 'export-file-list
                   (substring status (string-match pattern status start)
                              (match-end 0))))
      (setq start (match-end 0))))

(defun export-get-all-org-file (base-dirs)
  (defun export-get-org-file (base-dir)
    (dolist (filename (directory-files base-dir t "^\\w+"))
      (if (file-directory-p filename) (export-get-org-file filename)
        (when (string-equal (file-name-extension filename) "org")
          (message filename)
          (add-to-list 'export-file-list filename)))))
  (dolist (base-dir base-dirs) (export-get-org-file base-dir)))

(defun export-html-by-file-name (file-name)
  (if (file-exists-p file-name)
      (progn
        (setq work-buffer (or (find-buffer-visiting file-name)
                              (find-file-noselect file-name)))
        (princ (format "Export %s...\n" file-name))
        (with-current-buffer work-buffer (org-html-export-to-html))
        (kill-buffer work-buffer))))

(defun export-read-file-text (file-name)
  (with-temp-buffer
    (insert-file-contents-literally file-name)
    (decode-coding-region (point-min) (point-max) 'utf-8 t)))

;; Refrence https://coldnew.github.io/a1ed40e3/
(defadvice org-html-paragraph (before org-html-paragraph-advice
                                      (paragraph contents info) activate)
  "Join consecutive Chinese lines into a single long line without
unwanted space when exporting org-mode to html."
  (let* ((origin-contents (ad-get-arg 1))
         (fix-regexp "[[:multibyte:]]")
         (fixed-contents
          (replace-regexp-in-string
           (concat
            "\\(" fix-regexp "\\) *\n *\\(" fix-regexp "\\)") "\\1\\2" origin-contents)))
    (ad-set-arg 1 fixed-contents)))

