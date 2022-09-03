$(document).on('click', '.save-btn', savePost)


async function savePost(e) {
  e.stopPropagation()

  const title = $(this).data('title')
  const url = $(this).data('url')
  const username = $(this).data('user')
  const redditID = $(this).data('id')

  console.log('USERNAME => ', username)
  console.log('URL: ', url)
  console.log('TITLE: ', title)
  console.log('REDDIT ID => ', redditID)
  
  await axios({
    method: 'post',
    url: `/users/${username}/save/`,
    data: {
      title,
      url,
      username,
      id: redditID
    }
  })

  // toggle star icon
  $(this).find('i').toggleClass('fa-regular fa-solid')
  
  // find duplicate ID and toggle class too
  findMatchingID(redditID)
}

// removes focus highlighting on buttons
$('.btn').mouseup(function () {
  this.blur()
})


// refresh favs tab on click
$('#favs-tab').click(function(e) {
  e.stopPropagation()
  $("#accordionFavs").load(" #accordionFavs > *");
  console.log('testing this')
})


// finds all elements with matching ID and toggle class for first one
function findMatchingID(id) {
  const starBtn = $(".accordion-header").not(this).find(`[data-id='${id}']`).find('i')

  if (!starBtn) return;

  if (starBtn.length === 2) {
    starBtn.eq(0).toggleClass('fa-regular fa-solid')
  }
}


// for bootstrap tooltips
const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))