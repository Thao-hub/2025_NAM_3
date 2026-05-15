(function () {
  function attachSwipe(container, onPrev, onNext) {
    let startX = 0;
    let deltaX = 0;

    container.addEventListener("touchstart", function (event) {
      const touch = event.changedTouches && event.changedTouches[0];
      if (!touch) return;
      startX = touch.clientX;
      deltaX = 0;
    }, { passive: true });

    container.addEventListener("touchmove", function (event) {
      const touch = event.changedTouches && event.changedTouches[0];
      if (!touch) return;
      deltaX = touch.clientX - startX;
    }, { passive: true });

    container.addEventListener("touchend", function () {
      if (Math.abs(deltaX) < 40) return;
      if (deltaX < 0) {
        onNext();
      } else {
        onPrev();
      }
      deltaX = 0;
    }, { passive: true });
  }

  function initOverlayGallery(gallery) {
    const images = Array.from(gallery.querySelectorAll("img"));
    const dots = Array.from(gallery.querySelectorAll(".product-media-dots span"));
    if (images.length < 2) return;

    let index = 0;
    let timer = null;
    const delay = Number(gallery.dataset.autoplayMs || 5000);

    function render(nextIndex) {
      images[index].classList.remove("is-active");
      if (dots[index]) dots[index].classList.remove("is-active");
      index = (nextIndex + images.length) % images.length;
      images[index].classList.add("is-active");
      if (dots[index]) dots[index].classList.add("is-active");
    }

    function next() {
      render(index + 1);
    }

    function prev() {
      render(index - 1);
    }

    function restart() {
      if (timer) window.clearInterval(timer);
      timer = window.setInterval(next, delay);
    }

    dots.forEach(function (dot, dotIndex) {
      dot.style.cursor = "pointer";
      dot.addEventListener("click", function (event) {
        event.preventDefault();
        render(dotIndex);
        restart();
      });
    });

    attachSwipe(gallery, function () {
      prev();
      restart();
    }, function () {
      next();
      restart();
    });

    restart();
  }

  function initDetailGallery(gallery) {
    const mainImage = gallery.querySelector("[data-gallery-main]");
    const thumbs = Array.from(gallery.querySelectorAll("[data-gallery-thumb]"));
    if (!mainImage || thumbs.length < 2) return;

    let index = thumbs.findIndex(function (thumb) {
      return thumb.classList.contains("is-active");
    });
    if (index < 0) index = 0;
    let timer = null;
    const delay = Number(gallery.dataset.autoplayMs || 5000);

    function render(nextIndex) {
      index = (nextIndex + thumbs.length) % thumbs.length;
      const activeThumb = thumbs[index];
      mainImage.src = activeThumb.dataset.imageUrl || mainImage.src;
      mainImage.alt = activeThumb.dataset.imageAlt || mainImage.alt;
      thumbs.forEach(function (thumb) {
        thumb.classList.remove("is-active");
      });
      activeThumb.classList.add("is-active");
    }

    function next() {
      render(index + 1);
    }

    function prev() {
      render(index - 1);
    }

    function restart() {
      if (timer) window.clearInterval(timer);
      timer = window.setInterval(next, delay);
    }

    thumbs.forEach(function (thumb, thumbIndex) {
      thumb.addEventListener("click", function () {
        render(thumbIndex);
        restart();
      });
    });

    attachSwipe(gallery, function () {
      prev();
      restart();
    }, function () {
      next();
      restart();
    });

    restart();
  }

  window.initProductGalleries = function () {
    document.querySelectorAll("[data-product-gallery]").forEach(function (gallery) {
      if (gallery.dataset.galleryReady === "1") return;
      gallery.dataset.galleryReady = "1";
      if (gallery.querySelector("[data-gallery-main]")) {
        initDetailGallery(gallery);
      } else {
        initOverlayGallery(gallery);
      }
    });
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", window.initProductGalleries);
  } else {
    window.initProductGalleries();
  }
})();
