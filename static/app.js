$(document).on('click', '.save-btn', savePost)


// allow user to save/unsave a post
async function savePost(e) {
  e.stopPropagation()

  const title = $(this).data('title')
  const url = $(this).data('url')
  const username = $(this).data('user')
  const redditID = $(this).data('id')
  const comments = $(this).data('comments')
  
  await axios({
    method: 'post',
    url: `/users/${username}/save/`,
    data: {
      title,
      url,
      username,
      id: redditID,
      comments
    }
  })

  // removes focus highlighting on button
  $(this).blur()
  
  // find duplicate ID and toggle class too
  findMatchingID(redditID)
}


// refresh favs tab on click
$('#favs-tab').click(function(e) {
  e.stopPropagation()

  $("#accordionFavs").load(" #accordionFavs > *");
})


// finds all elements with matching ID and toggle class for first one
function findMatchingID(id) {
  const starBtn = $(".accordion-header").not(this).find(`[data-id='${id}']`).find('i')

  if (!starBtn) return; // quit if undefined
  
  if (starBtn.length === 2) {
    starBtn.eq(0).toggleClass('fa-regular fa-solid')
    starBtn.eq(1).toggleClass('fa-regular fa-solid')
  } else if (starBtn.length === 1) {
    starBtn.toggleClass('fa-regular fa-solid')
  }
}


// confirm account deletion
$('#btn-delete').click(() => confirm('Are you sure you want to delete your account?'))

// for flash messages
if ($('.flash-msg').length > 0) {
  $(".flash-msg").show().delay(3500).fadeOut('slow');
} else {
  $(".flash-msg").hide()
}

// for bootstrap tooltips
const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))