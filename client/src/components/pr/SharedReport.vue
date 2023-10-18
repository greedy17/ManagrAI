<template>
  <div v-if="this.report" class="reports">
    <div class="pdf-slide-container">
      <div class="pdf-overlay">
        <div>
          <h1>{{ report.title }}</h1>
        </div>

        <div style="margin-right: 16px" class="mar-top managr">
          <small> Created by: </small>
          <p>
            <span
              ><img
                class="blue-filter"
                style="margin-bottom: -2px"
                src="@/assets/images/logo.png"
                height="20px"
                alt="" /></span
            >managr
          </p>
        </div>
      </div>

      <img class="pdf-slide-image" :src="report.main_image" alt="" />
    </div>

    <div class="divider off-bg no-border">
      <p class="divider-text off-bg no-border center-media">Summary</p>
    </div>

    <div class="main off-bg">
      <div>
        <pre class="pre-text" v-html="report.meta_data.summary"></pre>
      </div>
    </div>

    <div class="divider">
      <p class="divider-text center-media">Media Clips</p>
    </div>

    <div class="main main-mobile white-bg">
      <section v-if="categoryClips">
        <div v-for="(category, catName) in categoryClips" :key="catName">
          <h2 class="category-name">{{ catName }}</h2>
          <div v-for="(clip, i) in category" :key="i" class="news-card">
            <header>
              <!-- <div>{{ categoryClips }}</div> -->
              <div class="card-col">
                <div class="card-top-left">
                  <span>{{
                    clip.source ? (clip.source.name ? clip.source.name : clip.source) : 'Tweet'
                  }}</span>
                </div>
                <div class="article-title-container">
                  <img
                    v-if="clip.user"
                    class="user-profile-img"
                    :src="clip.user.profile_image_url"
                  />
                  <h1 class="article-title" @click="goToArticle(clip.link)">
                    {{ clip.title ? clip.title : clip.user.name }}
                  </h1>
                </div>
                <p class="article-preview">
                  {{ clip.description ? clip.description : clip.text }}
                </p>
                <div
                  v-if="clip.attachments && clip.attachments.mediaURLs"
                  class="tweet-attachement display-flex"
                >
                  <div
                    style="margin-bottom: 16px"
                    v-for="mediaURL in clip.attachments.mediaURLs"
                    :key="mediaURL.url"
                    class="mar-right"
                  >
                    <div v-if="mediaURL.type === 'video'">
                      <video style="margin-top: 1rem" width="400" controls>
                        <source :src="mediaURL.url" type="video/mp4" />
                      </video>
                    </div>
                    <div v-else-if="mediaURL.type === 'animated_gif'">
                      <video style="margin-top: 1rem" width="400" autoplay loop muted playsinline>
                        <source :src="mediaURL.url" type="video/mp4" />
                      </video>
                    </div>
                    <div v-else>
                      <img :src="mediaURL.url" class="cover-photo-no-l-margin" alt="" />
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="!clip.edit_history_tweet_ids" @click="goToArticle(clip.link)">
                <img :src="clip.image_url" class="cover-photo" />
              </div>
            </header>

            <div class="card-footer">
              <div class="author-time">
                <span class="author"
                  >@{{
                    clip.author
                      ? clip.author
                      : clip.user && clip.user.username
                      ? clip.user.username
                      : ''
                  }}</span
                >
                <span class="divier-dot">.</span>
                <small v-if="clip.user && clip.user.public_metrics" class="bold-text"
                  >{{ formatNumber(clip.user.public_metrics.followers_count) }}
                  <span>Followers</span>
                </small>
                <span class="divier-dot">.</span>
                <span class="off-gray">{{
                  getTimeDifferenceInMinutes(
                    clip.publish_date ? clip.publish_date : clip.created_at,
                  )
                }}</span>
              </div>
            </div>
            <div v-if="clip.summary">
              <pre v-html="clip.summary" class="pre-text blue-bg"></pre>
            </div>
          </div>
        </div>
      </section>
      <section v-else>
        <div v-for="(clip, i) in report.meta_data.clips" :key="i" class="news-card">
          <header>
            <!-- <div>{{ categoryClips }}</div> -->
            <div class="card-col">
              <div class="card-top-left">
                <span>{{
                  clip.source ? (clip.source.name ? clip.source.name : clip.source) : 'Tweet'
                }}</span>
              </div>
              <div class="article-title-container">
                <img v-if="clip.user" class="user-profile-img" :src="clip.user.profile_image_url" />
                <h1 class="article-title" @click="goToArticle(clip.link)">
                  {{ clip.title ? clip.title : clip.user.name }}
                </h1>
              </div>
              <p class="article-preview">
                {{ clip.description ? clip.description : clip.text }}
              </p>
              <div
                v-if="clip.attachments && clip.attachments.mediaURLs"
                class="tweet-attachement display-flex"
              >
                <div
                  style="margin-bottom: 16px"
                  v-for="mediaURL in clip.attachments.mediaURLs"
                  :key="mediaURL.url"
                  class="mar-right"
                >
                  <div v-if="mediaURL.type === 'video'">
                    <video style="margin-top: 1rem" width="400" controls>
                      <source :src="mediaURL.url" type="video/mp4" />
                    </video>
                  </div>
                  <div v-else-if="mediaURL.type === 'animated_gif'">
                    <video style="margin-top: 1rem" width="400" autoplay loop muted playsinline>
                      <source :src="mediaURL.url" type="video/mp4" />
                    </video>
                  </div>
                  <div v-else>
                    <img :src="mediaURL.url" class="cover-photo-no-l-margin" alt="" />
                  </div>
                </div>
              </div>
            </div>

            <div v-if="!clip.edit_history_tweet_ids" @click="goToArticle(clip.link)">
              <img :src="clip.image_url" class="cover-photo" />
            </div>
          </header>

          <div class="card-footer">
            <div class="author-time">
              <span class="author"
                >@{{
                  clip.author
                    ? clip.author
                    : clip.user && clip.user.username
                    ? clip.user.username
                    : ''
                }}</span
              >
              <span class="divier-dot">.</span>
              <small v-if="clip.user && clip.user.public_metrics" class="bold-text"
                >{{ formatNumber(clip.user.public_metrics.followers_count) }}
                <span>Followers</span>
              </small>
              <span class="divier-dot">.</span>
              <span class="off-gray">{{
                getTimeDifferenceInMinutes(clip.publish_date ? clip.publish_date : clip.created_at)
              }}</span>
            </div>
          </div>
          <div v-if="clip.summary">
            <pre v-html="clip.summary" class="pre-text blue-bg"></pre>
          </div>
        </div>
      </section>
    </div>

    <div class="report-footer">
      <div class="branding">
        <p>{{ formatDate(reportDate) }}</p>
      </div>
    </div>
  </div>
</template>
<script>
import User from '@/services/users'

export default {
  name: 'SharedReport',
  data() {
    return {
      report: null,
      code: null,
      imageUrl: null,
      reportDate: null,
    }
  },
  props: {
    clips: {},
  },
  async created() {
    if (this.$route.params.code) {
      let code = this.$route.params.code
      this.code = code
      try {
        await User.api.getReport(code).then((response) => {
          this.report = response.data
          this.reportDate = response.date
        })
      } catch (e) {
        console.log(e)
      }
    }
  },
  methods: {
    formatDate(dateString) {
      // Create a new Date object in UTC
      const date = new Date(dateString)

      // Get the various components
      const day = date.getUTCDate()
      const year = date.getUTCFullYear()

      // Get the month name
      const monthNames = [
        'January',
        'February',
        'March',
        'April',
        'May',
        'June',
        'July',
        'August',
        'September',
        'October',
        'November',
        'December',
      ]

      const monthName = monthNames[date.getUTCMonth()]

      // Assemble the final string
      return `${monthName} ${day}, ${year}`
    },
    formatNumber(num) {
      if (num >= 1000000000) {
        return (num / 1000000000).toFixed(1).replace(/\.0$/, '') + 'B'
      }
      if (num >= 1000000) {
        return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M'
      }
      if (num >= 1000) {
        return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'K'
      }
      return num.toString()
    },
    getTimeDifferenceInMinutes(dateString) {
      if (dateString) {
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
          let month
          let day
          let year
          if (Number(givenDate.getMonth() + 1)) {
            month = givenDate.getMonth() + 1
          } else {
            month = '--'
          }
          if (Number(givenDate.getDate())) {
            day = givenDate.getDate()
          } else {
            day = '--'
          }
          if (Number(givenDate.getFullYear())) {
            year = givenDate.getFullYear()
          } else {
            year = '--'
          }
          return `${month}/${day}/${year}`
        }
      } else {
        return '--/--/----'
      }
    },

    goToArticle(link) {
      if (link) {
        window.open(link, '_blank')
      }
    },
  },
  computed: {
    categoryClips() {
      const clips = this.report.meta_data.clips
      if (clips[0].category) {
        const categories = {}
        for (let i = 0; i < clips.length; i++) {
          console.log('clips[i]', clips[i])
          console.log('categories', categories)
          if (categories[clips[i].category]) {
            categories[clips[i].category] = [...categories[clips[i].category], clips[i]]
          } else {
            categories[clips[i].category] = [clips[i]]
          }
        }
        return categories
      }
    },
  },
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.reports {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  height: 100vh;
  background-color: white;
  color: $base-gray;
  font-family: $thin-font-family;
  overflow-y: scroll;
  @media only screen and (max-width: 600px) {
    height: 90vh;
  }
}
.reports::-webkit-scrollbar {
  width: 0;
  height: 0px;
}

.reports::-webkit-scrollbar-thumb {
  background-color: transparent;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.reports:hover::-webkit-scrollbar-thumb {
  background-color: $mid-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

section {
  margin-top: 32px;
}

header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 32px;
  min-height: 120px;
  overflow: none;
  text-overflow: ellipsis;
  margin-bottom: 2rem;
}

.pdf-slide-container {
  width: 100vw;
  height: 70vh;
  position: relative;
}

.pdf-overlay {
  position: absolute;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: flex-end;
  height: 100%;
  width: 100%;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.75), transparent);

  p,
  h1 {
    margin: 0;
    padding: 0 0 32px 16px;
    font-family: $thin-font-family;
    font-weight: 400;
    color: $off-white;
  }

  h1 {
    font-size: 24px;
  }
}

.pdf-slide-image {
  width: 100%;
  height: 100%;
  // box-shadow: 26px 30px 64px rgba(0, 0, 0, 0.1);
  object-fit: cover;
}

.main {
  padding: 32px 15vw 64px 15vw;
}

.main-mobile {
  @media only screen and (max-width: 600px) {
    padding: 32px 10px 64px 10px;
  }
}

.pre-text {
  color: $dark-black-blue;
  font-family: $thin-font-family;
  font-size: 17px;
  line-height: 32px;
  word-wrap: break-word;
  white-space: pre-wrap;
  padding: 16px 0;
}

.divider {
  position: relative;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  width: 100%;
}

.divider-text {
  position: absolute;
  top: -36px;
  left: 46%;
  z-index: 20;
  background-color: white;
  padding: 6px 18px;
  border-radius: 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  font-size: 22px;
}

.center-media {
  left: 45%;
  @media only screen and (max-width: 600px) {
    left: 32.5%;
  }
}

.off-bg {
  background-color: $off-white;
}

.white-bg {
  background-color: white;
}

.news-card {
  position: relative;
  min-height: 220px;
  width: 100%;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
  padding: 1rem 0;
  margin-bottom: 1rem;
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
.article-title {
  font-size: 16px;
  font-weight: 900;
  line-height: 24px;
  letter-spacing: 0;
  color: $base-gray;
  margin: 12px 0;
  max-width: 500px;
  white-space: nowrap;
  display: inline;
  text-overflow: ellipsis;
  overflow: hidden;
  cursor: pointer;
  padding: 0;

  &:hover {
    color: #6b6b6b;
  }
  @media only screen and (max-width: 600px) {
    max-width: 50vw;
  }
}

.article-preview {
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 16px;
  height: 68px;
  line-height: 24px;
  display: inline;
  text-overflow: ellipsis;
  overflow: hidden;
  font-weight: 400;
  margin: 0;
}

.cover-photo {
  height: 112px;
  width: 116px;
  margin-left: 1rem;
  margin-top: 1.25rem;
  border-radius: 4px;
  object-fit: cover;
  cursor: pointer;

  &:hover {
    opacity: 0.7;
  }
}
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  margin-top: 1rem;
  span {
    font-size: 13px;
    margin-right: 0.5rem;
  }
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

.author {
  display: inline-block;
  overflow: hidden;
  white-space: nowrap;
  max-width: 200px;
  min-height: 22px;
  text-overflow: ellipsis;
  background-color: $soft-gray;
  padding: 4px 12px;
  color: $base-gray;
  border-radius: 12px;
}

.off-gray {
  color: #6b6b6b;
}

.blue-bg {
  background-color: $white-blue;
  padding: 16px;
  border-radius: 4px;
}

.mar-top {
  margin-top: 16px !important;
}

.no-border {
  border-bottom: 1px solid transparent !important;
  box-shadow: none !important;
}

.report-footer {
  width: 100vw;
  position: relative;
  background-color: red;
}

.branding {
  padding: 32px 0 104px 0;
  font-size: 18px;
  position: absolute;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  width: 100%;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.15), transparent);
  font-family: $thin-font-family;
  p,
  h2 {
    margin: 0;
    font-weight: 400;
  }
  p {
    font-size: 20px;
    color: $dark-black-blue;
  }
  small {
    font-size: 16px;
  }
}

.row {
  display: flex;
  align-items: center;
  justify-content: center;
}

.blue-filter {
  filter: brightness(0) invert(100%);
  opacity: 0.7;
  //  sepia(33%) saturate(348%) hue-rotate(161deg) brightness(91%)
  //   contrast(90%);
}

.managr {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  font-weight: 400;

  p {
    font-family: $thin-font-family !important;
    opacity: 0.7;
    font-size: 28px;
    span {
      margin-bottom: -2px;
    }
  }
  small {
    opacity: 0.7;
    font-size: 12px;
    color: white;
  }
}
.article-title-container {
  display: flex;
  align-items: center;
}
.user-profile-img {
  height: 18px;
  margin-right: 0.5rem;
  // margin-top: 0.25rem;
}
.tweet-attachement {
  img {
    @media only screen and (max-width: 600px) {
      width: 80vw;
    }
  }
  video {
    @media only screen and (max-width: 600px) {
      width: 80vw;
    }
  }
}
.cover-photo-no-l-margin {
  height: 112px;
  width: 116px;
  margin-top: 1.25rem;
  object-fit: cover;
  cursor: text;
  border-radius: 4px;
}
.display-flex {
  display: flex;
}
.mar-right {
  margin-right: 1rem;
}
.category-name {
  font-family: $thin-font-family;
  font-size: 22px;
  margin-left: -0.5rem;
}
</style>