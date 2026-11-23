(() => {
  const imageSelector =
    ".md-typeset img.book-figure-image, .md-typeset .readme-page table img";

  let dialog = null;
  let previewImg = null;
  let captionEl = null;
  let activeSourceImg = null;

  const getCaptionText = (img) => {
    const itemNote = img
      .closest(".book-figure-item")
      ?.querySelector(".book-figure-note")
      ?.textContent?.trim();
    const figCaption = img
      .closest("figure")
      ?.querySelector("figcaption")
      ?.textContent?.trim();
    if (itemNote && figCaption && !figCaption.includes(itemNote)) {
      return `${figCaption}（${itemNote}）`;
    }
    if (figCaption) return figCaption;
    if (itemNote) return itemNote;
    return img.getAttribute("alt")?.trim() ?? "";
  };

  const updatePreviewSize = (sourceImg) => {
    if (!previewImg || !sourceImg) return;
    const rect = sourceImg.getBoundingClientRect();
    const naturalWidth = sourceImg.naturalWidth || rect.width || 800;
    const naturalHeight = sourceImg.naturalHeight || rect.height || 600;
    const aspect = naturalWidth / Math.max(naturalHeight, 1);

    const maxWidth = Math.min(window.innerWidth * 0.92, 1280);
    const maxHeight = window.innerHeight * 0.82;
    const src = sourceImg.currentSrc || sourceImg.src || "";
    const isSvg = /\.svg($|[?#])/i.test(src);

    const desiredWidth = isSvg
      ? maxWidth
      : Math.max(naturalWidth, Math.round(rect.width * 1.75), 760);
    const desiredHeight = desiredWidth / aspect;
    const scale = Math.min(1, maxWidth / desiredWidth, maxHeight / desiredHeight);
    const finalWidth = Math.max(1, Math.round(desiredWidth * scale));

    previewImg.style.width = `${finalWidth}px`;
  };

  const ensureDialog = () => {
    if (dialog) return dialog;

    dialog = document.createElement("dialog");
    dialog.className = "book-image-lightbox";
    dialog.setAttribute("aria-label", "图片放大预览");

    const figure = document.createElement("figure");
    figure.className = "book-image-lightbox__figure";

    previewImg = document.createElement("img");
    previewImg.className = "book-image-lightbox__image";
    previewImg.alt = "";

    captionEl = document.createElement("figcaption");
    captionEl.className = "book-image-lightbox__caption";

    figure.append(previewImg, captionEl);
    dialog.append(figure);
    document.body.append(dialog);

    dialog.addEventListener("click", () => {
      dialog.close();
    });

    dialog.addEventListener("close", () => {
      document.documentElement.classList.remove("book-lightbox-open");
      activeSourceImg = null;
    });

    window.addEventListener("resize", () => {
      if (dialog?.open && activeSourceImg) {
        updatePreviewSize(activeSourceImg);
      }
    });

    return dialog;
  };

  document.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLImageElement)) return;
    if (!target.matches(imageSelector)) return;
    if (target.closest("a")) return;

    const modal = ensureDialog();
    const src = target.currentSrc || target.src;
    if (!src) return;

    activeSourceImg = target;
    previewImg.src = src;
    previewImg.alt = target.alt || "";
    updatePreviewSize(target);

    const caption = getCaptionText(target);
    captionEl.textContent = caption;
    captionEl.hidden = !caption;

    document.documentElement.classList.add("book-lightbox-open");
    if (!modal.open) {
      modal.showModal();
    }
  });
})();
