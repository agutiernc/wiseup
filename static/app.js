$('.save-btn').click(savePost)

async function savePost(e) {
  /// e.preventDefault()

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
    url: `/users/${username}/save`,
    data: {
      title,
      url,
      username,
      id: redditID
    }
  })
}