<template>
  <div class="main-content">
    <div class="card-container">
      <div v-if="loading" class="loader-container">
        <div class="loader-row">
          <div class="loading">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
          </div>
        </div>
      </div>
      <div v-else-if="filteredArticles.length">
        <div v-for="article in filteredArticles" :key="article.id" class="news-container">
          <div class="news-card" @click="selectArticle(article)">
            <header>
              <div class="card-col">
                <div class="card-top-left">
                  <!-- <img :src="article.icon" /> -->
                  <span>{{ article.source.name }}</span>
                </div>
                <h1 class="article-title" @click="goToArticle(article.url)">
                  {{ article.title }}
                </h1>
                <p @click="getArticleSummary(article.url)" class="article-preview">
                  {{ article.description }}
                </p>
              </div>

              <div @click="goToArticle(article.link)">
                <img :src="article.urlToImage" class="cover-photo" />
              </div>
            </header>

            <div class="card-footer">
              <div class="author-time">
                <span class="author">{{ article.author }}</span>
                <span class="divier-dot">.</span>
                <span class="off-gray">{{ getTimeDifferenceInMinutes(article.publishedAt) }}</span>
              </div>
              <div class="footer-icon-container">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" class="left-mar">
                  <path
                    d="M17.5 1.25a.5.5 0 0 1 1 0v2.5H21a.5.5 0 0 1 0 1h-2.5v2.5a.5.5 0 0 1-1 0v-2.5H15a.5.5 0 0 1 0-1h2.5v-2.5zm-11 4.5a1 1 0 0 1 1-1H11a.5.5 0 0 0 0-1H7.5a2 2 0 0 0-2 2v14a.5.5 0 0 0 .8.4l5.7-4.4 5.7 4.4a.5.5 0 0 0 .8-.4v-8.5a.5.5 0 0 0-1 0v7.48l-5.2-4a.5.5 0 0 0-.6 0l-5.2 4V5.75z"
                    fill="#000"
                  ></path>
                </svg>
                <img src="@/assets/images/sparkles-thin.svg" class="right-arrow-footer" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="empty-container">
        <button @click="getClips" class="large-dark-button">
          <img src="@/assets/images/sparkle.svg" height="14px" alt="" />
          Create a new search
        </button>
      </div>
    </div>
  </div>
</template>
<script>
import ChatTextBox from '../Chat/ChatTextBox.vue'
import Comms from '@/services/comms'

export default {
  name: 'SummariesMainContent',
  components: {
    ChatTextBox,
  },
  data() {
    return {
      loading: false,
      submitting: false,
      summaryLoading: false,
      summary: null,
      articles: [],
      selectedSearch: '',
      currentDate: new Date(),
      summaryChat: 'SUMMARY',
      filterText: '',
      message: '',
      newSummary: false,
      selectedArticles: [],
      filteredArticles: [],
      searchModalOpen: false,
      actions: [
        {
          name: 'Summarize',
          value: 'Summarize...',
        },
        { name: 'Generate', value: 'Generate...' },
        { name: 'Ask Managr', value: 'Ask managr... ' },
      ],
    }
  },
  watch: {},
  created() {},
  methods: {
    toggleSearchModal() {
      this.searchModalOpen = !this.searchModalOpen
    },
    async getArticleSummary(url, instructions = null) {
      console.log(url)
      try {
        await Comms.api
          .getArticleSummary({
            url: url,
            search: 'Houston Rockets',
            instructions: instructions,
          })
          .then((response) => {
            console.log(response)
          })
      } catch (e) {
        console.log(e)
      }
    },
    async getClips() {
      this.loading = true
      try {
        await Comms.api
          .getClips({
            search: 'Houston Rockets',
          })
          .then((response) => {
            this.filteredArticles = response.articles
            this.selectedSearch = 'Houston Rockets'
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.loading = false
      }
    },
    getTimeDifferenceInMinutes(dateString) {
      const currentDate = new Date()
      const givenDate = new Date(dateString)

      if (
        givenDate.getDate() === currentDate.getDate() &&
        givenDate.getMonth() === currentDate.getMonth() &&
        givenDate.getFullYear() === currentDate.getFullYear()
      ) {
        const timeDifferenceInMilliseconds = currentDate - givenDate
        const timeDifferenceInMinutes = Math.floor(timeDifferenceInMilliseconds / (1000 * 60))
        if (timeDifferenceInMinutes >= 60) {
          const timeDifferenceInHours = Math.floor(timeDifferenceInMinutes / 60)
          const remainingMinutes = timeDifferenceInMinutes % 60
          return `${timeDifferenceInHours}h`
        } else {
          return `${timeDifferenceInMinutes}m`
        }
      } else {
        return `${givenDate.getMonth() + 1}/${givenDate.getDate()}/${givenDate.getFullYear()}`
      }
    },
    getArticleUrls(articles) {
      return articles.map((a) => a.url)
    },
    async getSummary(clips, search = '', instructions = '') {
      this.$emit('set-loader', true)
      this.summaryLoading = true
      const urls = this.getArticleUrls(clips)
      const data = {
        clips: urls,
        search,
        instructions,
      }
      try {
        await Comms.api.getSummary(data).then((response) => {
          if (response.summary) {
            this.$emit('set-summary', response.summary)
          } else {
            this.$emit('set-summary', response.error)
          }
        })
      } catch (e) {
        console.log('Error in getSummary', e)
        this.$toast('Something went wrong, please try again.', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.$emit('set-loader', false)
        this.summaryLoading = false
      }
    },
    regenNewSummary() {
      this.getSummary(this.filteredArticles, '', this.message)
      this.changeRegen()
      this.message = ''
    },
    changeSummaryChat(type) {
      this.summaryChat = type
      this.scrollToBottom()
    },
    selectArticle(article) {
      this.$store.dispatch('updateSelectedArticle', article)
    },
    saveSelectedArticles() {
      this.getSummary(this.selectedArticles)
      this.selectedArticles = []
      this.changeNew()
    },
    addRemoveSelectedArticles(article) {
      const existingArticle = this.selectedArticles.filter((ar) => ar.url === article.url)[0]
      if (existingArticle) {
        this.selectedArticles = this.selectedArticles.filter((ar) => ar.url !== article.url)
      } else {
        this.selectedArticles.push(article)
      }
    },
    goToArticle(link) {
      window.location.href = link
    },
    changeNew() {
      this.newSummary = !this.newSummary
    },
    searchTitles() {
      this.filteredArticles = this.articles.filter((article) =>
        article.title.includes(this.filterText),
      )
    },
    scrollToBottom() {
      setTimeout(() => {
        const chatWindow = this.$refs.chatWindow
        setTimeout(() => {
          chatWindow.scrollTop = chatWindow.scrollHeight
        }, 200)
      }, 0)
    },
  },
  computed: {
    messages() {
      return this.$store.state.messages
    },
    userName() {
      return this.$store.state.user.firstName
    },
  },
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.bar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-direction: row;
  position: sticky;
  top: 0;
  padding: 16px 12px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  width: 100%;
  height: 66px;
  background-color: white;
  z-index: 10;
}

small {
  font-size: 14px !important;
}

.main-content {
  display: flex;
  margin: 0;
  color: $dark-black-blue;
  height: 100vh;
  padding-left: 68px;
  padding-right: 68px;
  overflow: none;
  position: relative;
}

.search-results {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-left: 1rem;
  margin-right: 1rem;
  padding-left: 1rem;
}
.row {
  display: flex;
  align-items: center;
  flex-direction: row;
  gap: 24px;
}
.card-container {
  overflow-y: auto;
  padding-top: 58px;
  position: relative;
  width: 100%;
}

.current-search {
  cursor: pointer;
}

.empty-container {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  margin-top: -58px;
}

header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 32px;
  height: 120px;
  overflow: none;
  text-overflow: ellipsis;
  margin-bottom: 2rem;
}

.news-container {
  display: flex;
  align-items: center;
  padding-top: 0.5rem;
}

.author {
  display: inline-block;
  overflow: hidden;
  max-width: 150px;
  height: 26px;
  text-overflow: ellipsis;
  background-color: $soft-gray;
  padding: 4px 12px;
  color: $base-gray;
  border-radius: 12px;
}

.off-gray {
  color: #6b6b6b;
}

.news-card {
  position: relative;
  min-height: 220px;
  width: 100%;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
  padding: 1rem;
}

.spinning-load {
  animation: rotation 3s infinite linear;
  opacity: 0.3;
  cursor: not-allowed;
  margin-top: 1rem;
}

@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(359deg);
  }
}

.card-col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.card:hover {
  transform: scale(1.025);
}
.card-top-left {
  display: flex;
  font-size: 12px;
  img {
    height: 12px;
    margin-right: 0.5rem;
  }
}
.cover-photo {
  height: 112px;
  width: 116px;
  margin-left: 1rem;
  margin-top: 1.25rem;
  object-fit: cover;

  cursor: pointer;
}
.highlights-summary-container {
  border-bottom: 1px solid $soft-gray;
  height: 65vh;
  overflow-y: auto;
  padding: 0 1rem;
}
.summary-buttons-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 1rem;
}
.summary-button {
  @include gray-text-button();
  margin: 0 0.5rem;
  padding: 8px 16px;
  img {
    height: 12px;
    margin-right: 0.5rem;
  }
}
.large-dark-button {
  @include dark-blue-button();
  padding: 12px 16px;
  img {
    filter: invert(81%) sepia(38%) saturate(738%) hue-rotate(349deg) brightness(95%) contrast(88%);
    margin-right: 8px;
  }
}
.dark-button {
  @include dark-blue-button();
  padding: 8px;
  img {
    filter: invert(81%) sepia(38%) saturate(738%) hue-rotate(349deg) brightness(95%) contrast(88%);
    margin-right: 8px;
  }
}
.wide {
  width: 90%;
}
.article-title {
  font-size: 20px;
  font-weight: 1000;
  line-height: 24px;
  letter-spacing: 0;
  color: $base-gray;
  margin: 12px 0;
}

.article-preview {
  color: $base-gray;
  font-size: 16px;
  max-height: 72px;
  text-overflow: ellipsis;
  overflow: hidden;
  font-weight: 400;
  margin: 0;
}
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  margin-top: 1rem;
  span {
    font-size: 12px;
    margin-right: 0.5rem;
  }
}
.footer-icon-container {
  display: flex;
  align-items: center;
  margin-right: 8px;
}
.right-arrow-footer {
  height: 16px;
  margin-left: 1rem;
  cursor: pointer;
}
.left-mar {
  margin-left: 1rem;
}
.footer-icon {
  height: 24px;
  margin-left: 1rem;
  cursor: pointer;
}
.author-time {
  display: flex;
  align-items: center;
  color: $light-gray-blue;
}
.divier-dot {
  position: relative;
  bottom: 0.2rem;
}
.large-dot {
  font-size: 40px;
  bottom: 1.7rem;
  margin-right: 0.75rem;
}
.gray-background {
  display: flex;
  align-items: center;
  background-color: $soft-gray;
  height: 4vh;
  width: 11vw;
  border-radius: 8px;
}
.toggle-container {
  border: 1px solid $soft-gray;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 5vw;
  height: 3vh;
  border-radius: 8px;
  margin: 0 0.25rem;
  color: $light-gray-blue;
  p {
    margin: 0;
    font-size: 12px;
    // text-align: center;
  }
}
.active {
  background-color: $white;
  border-radius: 8px;
  color: $dark-black-blue;
}
.updated-time {
  font-size: 12px;
  color: $light-gray-blue;
  display: flex;
  justify-content: flex-end;
  margin-bottom: 0.5rem;
  margin-top: 0.5rem;
  margin-right: 1rem;
}
.search {
  height: 12px;
  margin-right: 0.5rem;
  filter: invert(20%);
}
.search-bar {
  // background-color: white;
  border: 1px solid $very-light-gray;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3px 6px;
  border-radius: 8px;
  // margin-top: 16px;
  height: 4vh;
}
[type='search']::-webkit-search-cancel-button {
  -webkit-appearance: none;
  appearance: none;
}
input[type='search'] {
  width: 6.5vw;
  letter-spacing: 0.75px;
  border: none;
  padding: 4px 0;
  margin: 0;
  background: none;
  font-size: 12px;
}
input[type='search']:focus {
  outline: none;
}
::placeholder {
  color: $very-light-gray;
  font-size: 12px;
}
.highlights {
  margin-top: 0;
  font-size: 16px;
}
.dot {
  height: 8px;
  width: 8px;
  margin: 0.275rem 0.5rem 0 0;
}
.overall {
  font-size: 16px;
}
.highlight-point {
  font-size: 14px;
  // word-spacing: 1.15px;
  line-height: 1.5;
}
.small-title-text {
  font-size: 14px;
  color: $light-gray-blue;
  img {
    height: 12px;
    margin-right: 0.5rem;
    filter: invert(81%) sepia(38%) saturate(738%) hue-rotate(349deg) brightness(95%) contrast(88%);
    // filter: invert(63%) sepia(9%) saturate(735%) hue-rotate(200deg) brightness(95%) contrast(92%);
  }
}
.chat-container {
  width: 100%;
  height: 75vh;
  overflow-y: auto;
}
.chat-window {
  min-height: 63vh;
}
.message-text {
  font-family: $base-font-family;
  word-wrap: break-word;
  white-space: pre-wrap;
  padding: 0;
  margin: 0;
}
.message-container {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  margin: 0;
  width: 100%;
  padding: 0 1.5rem;

  p {
    padding: 0;
    margin: 0;
  }

  &:hover {
    background-color: $off-white !important;
  }
}

.message-container:first-of-type {
  padding-top: 0.5rem;
}
.margin-top {
  // margin-top: 4rem;
  // height: 96%;
  // overflow-y: auto;
}
.container-padding {
  border-radius: 6px;
  padding: 0.5rem;
}

.ai-text-container {
  overflow: scroll;
  background-color: white;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  padding: 0 0.75rem;
  line-height: 1.75;
  position: relative;

  &:hover {
    background-color: $off-white !important;
  }
}

.text-container {
  overflow: scroll;
  padding: 0.25rem;
  margin: 0;
  line-height: 1.75;
}

.images {
  padding: 0;
  margin: 0 0.5rem 0 0;
}

.bottom {
  position: sticky;
  bottom: 0;
  left: 0;
}

.bottom-right {
  position: absolute;
  bottom: 0;
  right: 0;
}

.avatar {
  background-color: $purple;
  color: white;
  width: 22px;
  height: 22px;
  margin-right: 0.2rem;
  margin-top: 6px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.title-header {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  font-family: $base-font-family;
  background-color: white;

  h4,
  p {
    margin: 0;
    padding: 0.5rem;
    width: fit-content;
    // outline: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 6px;
    // background-color: white;
    font-size: 12px;
    letter-spacing: 0.4px;

    span {
      color: $light-gray-blue;
    }
  }
}

@media (max-width: 768px) {
  .chat-container {
    font-size: 14px;
  }
}

.green-filter {
  filter: brightness(0%) invert(64%) sepia(8%) saturate(2746%) hue-rotate(101deg) brightness(97%)
    contrast(82%);
}
.gold-filter {
  filter: invert(89%) sepia(43%) saturate(4130%) hue-rotate(323deg) brightness(90%) contrast(87%);
  animation: shimmer 2s;
  -webkit-mask: linear-gradient(-60deg, #000 30%, #0005, #000 70%) right/200% 100%;
}

.invert {
  filter: invert(95%);
}

.green {
  background-color: $dark-green !important;
  color: white !important;
  border: 1px solid $dark-green !important;
}

.loader-container {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
}

.loader-row {
  border-radius: 6px;
  padding: 0.25rem 0;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 6px;
  padding: 1.5rem 0.75rem;
}

.dot {
  width: 4px;
  height: 4px;
  margin: 0 5px;
  background: rgb(97, 96, 96);
  border-radius: 50%;
  animation: bounce 1.2s infinite ease-in-out;
}

.dot:nth-child(2) {
  animation-delay: -0.4s;
}

.dot:nth-child(3) {
  animation-delay: -0.2s;
}

.col-start {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.generate-container {
  padding: 0 1rem 0.5rem 4.5rem;
  background-color: white;
  width: 100%;
}

.generate-button {
  @include chat-button();
  padding: 0.6rem 0.8rem;
  margin-bottom: 0.5rem;
  img {
    margin-right: 0.5rem;
  }
}

.content-button {
  @include chat-button();
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  margin-right: 0.5rem;
  svg {
    margin-right: 0.5rem;
  }
}

.small-button {
  @include chat-button();
  border: 1px solid rgba(0, 0, 0, 0.1);
  background-color: transparent;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  border-radius: 5px;
  font-size: 12px;
  padding: 0.35rem;
  margin-left: 1rem;
  font-weight: normal;

  img {
    margin: 0;
    margin-right: 0.5rem;
  }
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
    opacity: 0;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.go-back {
  position: absolute;
  right: 0.5rem;
  top: -1.75rem;
  display: flex;
  flex-direction: row;
  align-items: center;
}

.back {
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  outline: 1px solid rgba(0, 0, 0, 0.1);
  color: $coral;
  width: 20px;
  height: 20px;
  border-radius: 3px;
  cursor: pointer;
  margin-left: 0.5rem;
  margin-right: 2px;
  font-size: 11px;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 3px 6px 0 $very-light-gray;
    scale: 1.025;
  }

  img {
    transform: rotate(180deg);
  }
}

.pointer {
  cursor: pointer;
}
// @keyframes typing {
//   from {
//     width: 0;
//   }
//   to {
//     width: 100%;
//   }
// }

// @keyframes blinking {
//   0% {
//     border-right-color: transparent;
//   }
//   50% {
//     border-right-color: rgb(66, 65, 65);
//   }
//   100% {
//     border-right-color: transparent;
//   }
// }

// .typed {
//   overflow: hidden;
//   white-space: nowrap;
//   width: 0;
//   animation: typing 1.5s steps(30, end) forwards, blinking 1s infinite;
//   border-right: 1px solid;
// }
.chat-button-container {
  display: flex;
  justify-content: center;
  margin-bottom: 0.5rem;
}
.chat-button {
  @include secondary-button();
  // width: 6rem;
  padding: 0.5rem 1.2rem;
  margin: 0 0.5rem;
}
.chat-border {
  background-color: $silver;
  padding: 0.25rem;
  border-radius: 4px;
}
.input-container {
  background-color: $white;
  padding: 0.5rem;
  border-radius: 4px;
  box-shadow: 0 0 3px $very-light-gray;
  input {
    border: none;
    outline: none;
    width: 95%;
  }
}
.provide-instructions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 1rem 0;
  font-size: 14px;
}
.back-arrow {
  height: 20px;
  cursor: pointer;
}
.gray {
  color: rgb(82, 80, 80);
}
.summarize {
  @include gray-text-button();
}
.summarize-disabled {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem 1rem;
  border-radius: 0.3rem;
  font-weight: bold;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  background-color: $soft-gray;
  border: 1px solid $soft-gray;
  color: $base-gray;
  font-size: 12px;
  transition: all 0.3s;
}
</style>