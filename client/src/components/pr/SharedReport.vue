<template>
  <div v-if="this.report" class="reports">
    <div class="pdf-slide-container">
      <div class="pdf-overlay">
        <div>
          <h1>
            <span>{{ report.title }}</span>
          </h1>
        </div>

        <!-- <div class="managr">
          <img
            class="bg-blend"
            style="margin-bottom: -2px"
            src="@/assets/images/newLogo.png"
            height="40px"
            alt=""
          />
        </div> -->
      </div>

      <img class="pdf-slide-image" :src="report.main_image" alt="" />
    </div>

    <div class="divider-text">
      <h1 class="center-media bold-txt">Summary</h1>
    </div>

    <div style="padding-bottom: 0" class="main">
      <div class="container">
        <pre class="pre-text" v-html="report.meta_data.summary"></pre>
      </div>
    </div>

    <div class="divider-text">
      <h1 class="center-media bold-txt">Traffic</h1>
    </div>

    <div style="width: 100vw" class="main">
      <div class="container">
        <div class="space-between bottom-margin">
          <div class="col">
            <p class="bold-txt medium-txt">Total coverage</p>
            <small>Number of news clips in this report</small>
          </div>

          <p class="bold-txt">{{ formatNumber(report.meta_data.clips.length) }}</p>
        </div>

        <div class="space-between bottom-margin">
          <div class="col">
            <p class="bold-txt medium-txt">Unique visitors</p>
            <small>The potential audience reached by your media coverage</small>
          </div>

          <div class="row">
            <img style="margin-right: 8px" src="@/assets/images/users.svg" height="16px" alt="" />
            <p class="bold-txt">{{ formatNumber(report.meta_data.totalVisits) }}</p>
          </div>
        </div>

        <div class="space-between">
          <div class="col">
            <p class="bold-txt medium-txt">Total shares</p>
            <small>Number of times content was shared on social media</small>
          </div>

          <section class="row img-mar">
            <div style="margin-right: 20px" class="row">
              <img src="@/assets/images/facebook.png" height="20px" alt="" />
              <p class="bold-txt">{{ report.meta_data.socialTotals.totalFacebookLikes }}</p>
            </div>
            <div style="margin-right: 20px" class="row">
              <img src="@/assets/images/twitter-x.svg" height="16px" alt="" />
              <p class="bold-txt">{{ report.meta_data.socialTotals.totalTwitterLikes }}</p>
            </div>
            <div style="margin-right: 20px" class="row">
              <img src="@/assets/images/reddit.svg" height="20px" alt="" />
              <p class="bold-txt">{{ report.meta_data.socialTotals.totalRedditLikes }}</p>
            </div>
            <div class="row">
              <img src="@/assets/images/pinterest.png" height="20px" alt="" />
              <p class="bold-txt">{{ report.meta_data.socialTotals.totalPinterestLikes }}</p>
            </div>
          </section>
        </div>
      </div>

      <div style="margin-top: 24px" class="container">
        <div class="col bottom-margin">
          <p class="bold-txt medium-txt">Media exposure over time</p>
          <small
            >Number of media clips <span class="bold-txt">per week</span> along with the potential
            reach</small
          >
        </div>
        <ReportLineChart
          :volume="report.meta_data.chartData.clipCountList"
          :reach="report.meta_data.chartData.usersList"
          :dates="report.meta_data.chartData.dateList"
        />
      </div>
    </div>

    <div class="divider-text">
      <h1 class="center-media bold-txt">Top Coverage</h1>
    </div>

    <div style="width: 100vw" class="main">
      <section>
        <div v-for="(article, i) in report.meta_data.starredArticles" :key="i" class="container">
          <div style="position: relative" class="container__top">
            <div style="margin-bottom: 12px">
              <img @error="onImageError($event)" :src="article.image" class="photo-header-small" />
            </div>

            <div class="space-between no-letter-margin">
              <div class="col">
                <p class="bold-txt">
                  {{ article.traffic ? removeDomain(article.traffic.target) : 'unknown' }}
                </p>
                <div style="margin-top: 8px" class="row">
                  <img
                    style="margin-right: 4px"
                    src="@/assets/images/profile.svg"
                    height="12px"
                    alt=""
                  />
                  <p>{{ article.author[0] ? article.author[0] : 'Unkown' }}</p>
                </div>
              </div>
              <small>{{ getTimeDifferenceInMinutes(article.date) }}</small>
            </div>

            <div style="margin: 20px 0">
              <a :href="article.url" target="_blank" class="bold-txt elipsis-text">
                {{ article.description }}</a
              >
            </div>

            <div class="space-between bottom-margin-m">
              <div class="row img-mar">
                <img src="@/assets/images/users.svg" height="14px" alt="" />
                <p class="bold-txt">
                  {{ article.traffic ? formatNumber(article.traffic.users) : 0 }}
                </p>
              </div>

              <section class="row img-mar">
                <div style="margin-right: 12px" class="row">
                  <img src="@/assets/images/facebook.png" height="14px" alt="" />
                  <p class="bold-txt">
                    {{
                      formatNumber(
                        report.meta_data.socialData[article.url] &&
                          report.meta_data.socialData[article.url][0]
                          ? report.meta_data.socialData[article.url][0]['total_facebook_shares']
                            ? report.meta_data.socialData[article.url][0]['total_facebook_shares']
                            : 0
                          : 0,
                      )
                    }}
                  </p>
                </div>
                <div style="margin-right: 16px" class="row">
                  <img
                    style="margin-right: 4px"
                    src="@/assets/images/twitter-x.svg"
                    height="14px"
                    alt=""
                  />
                  <p class="bold-txt">
                    {{
                      formatNumber(
                        report.meta_data.socialData[article.url] &&
                          report.meta_data.socialData[article.url][0]
                          ? report.meta_data.socialData[article.url][0]['twitter_shares']
                            ? report.meta_data.socialData[article.url][0]['twitter_shares']
                            : 0
                          : 0,
                      )
                    }}
                  </p>
                </div>
                <div style="margin-right: 16px" class="row">
                  <img src="@/assets/images/reddit.svg" height="14px" alt="" />
                  <p class="bold-txt">
                    {{
                      formatNumber(
                        report.meta_data.socialData[article.url] &&
                          report.meta_data.socialData[article.url][0]
                          ? report.meta_data.socialData[article.url][0]['total_reddit_engagements']
                            ? report.meta_data.socialData[article.url][0][
                                'total_reddit_engagements'
                              ]
                            : 0
                          : 0,
                      )
                    }}
                  </p>
                </div>

                <div class="row">
                  <img
                    style="margin-right: 4px"
                    src="@/assets/images/pinterest.png"
                    height="14px"
                    alt=""
                  />
                  <p class="bold-txt">
                    {{
                      formatNumber(
                        report.meta_data.socialData[article.url] &&
                          report.meta_data.socialData[article.url][0]
                          ? report.meta_data.socialData[article.url][0]['pinterest_shares']
                            ? report.meta_data.socialData[article.url][0]['pinterest_shares']
                            : 0
                          : 0,
                      )
                    }}
                  </p>
                </div>

                <!-- <div class="row">
                      <img src="@/assets/images/twitter-x.svg" height="12px" alt="" />
                      <p class="bold-txt">1,000</p>
                    </div>
                    <div class="row">
                      <img src="@/assets/images/reddit.svg" height="14px" alt="" />
                      <p class="bold-txt">10,000</p>
                    </div> -->
              </section>
            </div>
          </div>

          <div v-if="article.summary" class="report-body">
            <div style="margin-top: 12px">
              <pre v-html="article.summary" class="pre-text"></pre>
            </div>
          </div>

          <div v-else class="report-body">
            <div class="space-between" style="margin-top: 12px">
              <!-- <div></div>
                    <button
                      :disabled="summaryLoading"
                      @click="getArticleSummary(article.url)"
                      class="primary-button"
                    >
                      Summarize
                      <img
                        v-if="summaryLoading && loadingUrl === article.url"
                        style="margin-left: 6px"
                        class="rotation invert"
                        src="@/assets/images/loading.svg"
                        height="14px"
                        alt=""
                      />
                    </button> -->
            </div>
          </div>
        </div>
      </section>
    </div>

    <div class="divider-text">
      <h1 class="center-media bold-txt">All Coverage</h1>
    </div>

    <div style="width: 100vw" class="main">
      <section class="container">
        <div v-for="(article, i) in report.meta_data.clips" :key="i" class="article">
          <div class="space-between">
            <p class="bold-txt">
              {{ article.traffic ? removeDomain(article.traffic.target) : 'unknown' }}
            </p>
          </div>

          <div class="space-between-bottom">
            <div class="article-body">
              <!-- <h3 class="bold-txt">
                {{ article.title }}
              </h3> -->
              <div style="margin: 20px 0">
                <a :href="article.url" target="_blank" class="bold-txt elipsis-text">
                  {{ article.title }}</a
                >
              </div>

              <p class="report-body">
                {{ article.description }}
              </p>
            </div>

            <img @error="onImageError($event)" :src="article.image" class="photo-header-alt" />
          </div>

          <div style="margin-top: 12px" class="space-between bottom-border">
            <div class="row report-body">
              <div class="pill">
                <img src="@/assets/images/profile.svg" height="12px" alt="" />
                <p style="margin-right: 6px">
                  {{ article.author && article.author[0] ? article.author[0] : 'Unkown' }}
                </p>
              </div>

              <small>{{ getTimeDifferenceInMinutes(article.date) }}</small>
            </div>

            <div class="row small-text">
              <div style="margin-right: 16px" class="row img-mar">
                <img
                  style="margin-right: 4px"
                  src="@/assets/images/users.svg"
                  height="14px"
                  alt=""
                />
                <p class="bold-txt">
                  {{ article.traffic ? formatNumber(article.traffic.users) : 0 }}
                </p>
              </div>

              <div style="margin-right: 16px" class="row">
                <img
                  style="margin-right: 4px"
                  src="@/assets/images/facebook.png"
                  height="14px"
                  alt=""
                />
                <p class="bold-txt">
                  {{
                    formatNumber(
                      report.meta_data.socialData[article.url] &&
                        report.meta_data.socialData[article.url][0]
                        ? report.meta_data.socialData[article.url][0]['total_facebook_shares']
                          ? report.meta_data.socialData[article.url][0]['total_facebook_shares']
                          : 0
                        : 0,
                    )
                  }}
                </p>
              </div>
              <div style="margin-right: 16px" class="row">
                <img
                  style="margin-right: 4px"
                  src="@/assets/images/twitter-x.svg"
                  height="14px"
                  alt=""
                />
                <p class="bold-txt">
                  {{
                    formatNumber(
                      report.meta_data.socialData[article.url] &&
                        report.meta_data.socialData[article.url][0]
                        ? report.meta_data.socialData[article.url][0]['twitter_shares']
                          ? report.meta_data.socialData[article.url][0]['twitter_shares']
                          : 0
                        : 0,
                    )
                  }}
                </p>
              </div>
              <div style="margin-right: 16px" class="row">
                <img
                  style="margin-right: 4px"
                  src="@/assets/images/reddit.svg"
                  height="14px"
                  alt=""
                />
                <p class="bold-txt">
                  {{
                    formatNumber(
                      report.meta_data.socialData[article.url] &&
                        report.meta_data.socialData[article.url][0]
                        ? report.meta_data.socialData[article.url][0]['total_reddit_engagements']
                          ? report.meta_data.socialData[article.url][0]['total_reddit_engagements']
                          : 0
                        : 0,
                    )
                  }}
                </p>
              </div>

              <div class="row">
                <img
                  style="margin-right: 4px"
                  src="@/assets/images/pinterest.png"
                  height="14px"
                  alt=""
                />
                <p class="bold-txt">
                  {{
                    formatNumber(
                      report.meta_data.socialData[article.url] &&
                        report.meta_data.socialData[article.url][0]
                        ? report.meta_data.socialData[article.url][0]['pinterest_shares']
                          ? report.meta_data.socialData[article.url][0]['pinterest_shares']
                          : 0
                        : 0,
                    )
                  }}
                </p>
              </div>
            </div>
          </div>

          <!-- <div style="margin-top: 8px" class="space-between bottom-border">
                  <div></div>
                  <section class="row-even small-text img-mar">
                    <div class="row">
                      <img src="@/assets/images/facebook.png" height="14px" alt="" />
                      <p class="bold-txt">{{ formatNumber(article.traffic.social / 2) }}</p>
                    </div>
                     <div class="row">
                      <img src="@/assets/images/pinterest.png" height="14px" alt="" />
                      <p class="bold-txt">{{ formatNumber(article.traffic.social / 8) }}</p>
                    </div>
                    <div class="row">
                      <img src="@/assets/images/twitter-x.svg" height="12px" alt="" />
                      <p class="bold-txt">{{ formatNumber(article.traffic.social / 2) }}</p>
                    </div>
                    <div class="row">
                      <img src="@/assets/images/reddit.svg" height="14px" alt="" />
                      <p class="bold-txt">{{ formatNumber(article.traffic.social / 4) }}</p>
                    </div>
                   
                  </section>
                </div> -->
        </div>

        <!-- <div v-for="(clip, i) in report.meta_data.clips" :key="i" class="news-card">
          <header>
            <div class="card-col">
              <div class="card-top-left">
                <span>{{ clip.source }}</span>
              </div>
              <div class="article-title-container">
                <h1 class="article-title" @click="goToArticle(clip.url)">
                  {{ clip.title }}
                </h1>
              </div>
              <p class="article-preview">
                {{ clip.description }}
              </p>
            </div>
          </header>

          <div class="card-footer">
            <div class="author-time space-between">
              <div>
                <span class="author">{{ clip.author[0] }}</span>
                <span class="divier-dot">.</span>
                <span class="off-gray">{{ getTimeDifferenceInMinutes(clip.date) }}</span>
              </div>

              <small class="bold-txt row">
                <img
                  style="margin-right: 8px"
                  src="@/assets/images/users.svg"
                  height="16px"
                  alt=""
                />
                {{ formatNumber(clip.traffic.users) }}
              </small>
            </div>
          </div>

          <div class="space-between">
            <div></div>
            <div class="row">
              <div style="margin-right: 12px" class="row">
                <img src="@/assets/images/facebook.png" height="14px" alt="" />
                <p class="bold-txt">
                  {{
                    formatNumber(
                      report.meta_data.socialData[clip.url] &&
                        report.meta_data.socialData[clip.url][0]
                        ? report.meta_data.socialData[clip.url][0]['total_facebook_shares']
                          ? report.meta_data.socialData[clip.url][0]['total_facebook_shares']
                          : 0
                        : 0,
                    )
                  }}
                </p>
              </div>
              <div class="row">
                <img src="@/assets/images/reddit.svg" height="14px" alt="" />
                <p class="bold-txt">
                  {{
                    formatNumber(
                      report.meta_data.socialData[clip.url] &&
                        report.meta_data.socialData[clip.url][0]
                        ? report.meta_data.socialData[clip.url][0]['total_reddit_engagements']
                          ? report.meta_data.socialData[clip.url][0]['total_reddit_engagements']
                          : 0
                        : 0,
                    )
                  }}
                </p>
              </div>
            </div>
          </div>
      
        </div> -->
      </section>
    </div>

    <div class="report-footer">
      <div class="branding">
        <p>{{ formatDate(reportDate) }}</p>
      </div>
    </div>

    <!-- <div @click.stop="openPanel" :class="{ expanded: panelOpen }" class="floating-panel">
      <div v-outside-click="closePanel" class="fadein panel-options" v-show="panelOpen">
        <img src="@/assets/images/wand.svg" height="20px" alt="" />
        <img src="@/assets/images/wand.svg" height="20px" alt="" />
        <img src="@/assets/images/wand.svg" height="20px" alt="" />
      </div>
      <img src="@/assets/images/wand.svg" height="20px" alt="" />
    </div> -->
  </div>
</template>
<script>
import User from '@/services/users'
import ReportLineChart from '@/components/ReportLineChart.vue'

export default {
  name: 'SharedReport',
  data() {
    return {
      panelOpen: false,
      report: null,
      code: null,
      imageUrl: null,
      reportDate: null,
      logoPlaceholder: require('@/assets/images/iconlogo.png'),
    }
  },
  components: {
    ReportLineChart,
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
          console.log(response.data)
          this.report = response.data
          this.reportDate = response.date
        })
      } catch (e) {
        console.log(e)
      }
    }
  },
  methods: {
    openPanel() {
      this.panelOpen = true
    },
    closePanel() {
      this.panelOpen = false
    },
    removeDomain(url) {
      const domainRegex = /\.(com|net|org|gov|edu|co|io|biz|info|us)$/i

      return url.replace(domainRegex, '')
    },
    onImageError(event) {
      event.target.src = this.logoPlaceholder
    },
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

a {
  text-decoration: none;
  color: $dark-black-blue;
}

.floating-panel {
  position: absolute;
  right: 72px;
  bottom: 64px;
  box-shadow: 1px 3px 6px rgba(0, 0, 0, 0.2);
  border-radius: 100%;
  padding: 8px 10px;
  background: transparent;
  z-index: 100;
}

.expanded {
  border-radius: 20px !important;

  img {
    margin: 8px 0;
  }
}

.panel-options {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.pill {
  display: flex;
  flex-direction: row;
  align-items: center;
  background-color: $soft-gray;
  border-radius: 16px;
  padding: 3px 10px;
  margin-right: 8px;

  img {
    margin-right: 4px;
  }
  p {
    margin: 0 !important;
    font-size: 14px;
  }
}

.space-between-bottom {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: flex-end;
  width: 100%;
}

.photo-header-small {
  height: 400px;
  width: 100%;
  margin: 0;
  object-fit: cover;
  object-position: top;
  border-radius: 5px;
}

.container {
  background-color: white;
  padding: 20px;
  border-radius: 9px;
  // border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  margin-bottom: 32px;
  font-family: $thin-font-family;
  p {
    margin: 8px 0;
  }

  small {
    color: $base-gray;
  }

  &__top {
    border-bottom: 2px solid rgba(0, 0, 0, 0.05);
  }
}

.bottom-border {
  border-bottom: 2px solid rgba(0, 0, 0, 0.05);
  padding-bottom: 12px;
}

.img-mar {
  img {
    margin-right: 8px;
  }
}

.bottom-margin {
  margin-bottom: 24px;
}

.bg-blend {
  mix-blend-mode: multiply;
  background-color: $off-white;
}

.photo-header-alt {
  height: 150px !important;
  width: 150px !important;
  margin: 0;
  object-fit: cover;
  object-position: top;
  border-radius: 4px;
}

.bold-txt {
  font-family: $base-font-family;
}

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
  font-size: 16px;
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
  height: 100vh;
  position: relative;
}

.space-between {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.pdf-overlay {
  position: absolute;
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: flex-end;
  height: 100%;
  width: 100%;

  background: linear-gradient(to top, rgba(0, 0, 0, 0.75), transparent);

  div {
    padding-left: 16px;
    font-family: $thin-font-family;
  }

  h1 {
    color: $off-white;
    font-size: 40px;

    span {
      font-family: $base-font-family;
    }
  }
}

.pdf-slide-image {
  width: 100%;
  height: 100%;
  // box-shadow: 26px 30px 64px rgba(0, 0, 0, 0.1);
  object-fit: cover;
  object-position: top;
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
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 16px;
  line-height: 32px;
  word-wrap: break-word;
  white-space: pre-wrap;
}

::v-deep .pre-text {
  a {
    color: $grape;
    border-bottom: 1px solid $grape;
    font-family: $base-font-family;
    text-decoration: none;
    padding-bottom: 2px;

    &:hover {
      opacity: 0.7;
    }
  }

  strong,
  h1,
  h2,
  h3,
  h4 {
    font-family: $base-font-family;
    margin: 0;
    font-size: 18px;
  }

  h3 {
    font-size: 20px;
  }

  h1 {
    font-size: 22px;
  }

  ul {
    display: block;
    list-style-type: disc;
    margin-block-start: 0;
    margin-block-end: 0;
    margin-inline-start: 0px;
    margin-inline-end: 0px;
    padding-inline-start: 16px;
    unicode-bidi: isolate;
  }

  li {
    // margin-top: -32px;
    padding: 0;
  }
}

.divider {
  position: relative;
  // border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  width: 100%;
}

.divider-text {
  padding: 10px 16px;
  border-bottom: 2px solid rgba(0, 0, 0, 0.1);
  font-size: 24px;
  margin-bottom: 24px;

  h1 {
    margin: 24px 0;
  }
}

.center-media {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: white;
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
  font-family: $base-font-family;
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
  flex-direction: row;
  align-items: center;
}

.blue-filter {
  filter: brightness(0) invert(100%);
  opacity: 0.7;
  //  sepia(33%) saturate(348%) hue-rotate(161deg) brightness(91%)
  //   contrast(90%);
}

.article {
  padding: 16px;
}

.article-body {
  margin-bottom: 12px;
  margin-right: 32px;
  width: 100%;
  max-height: 150px;
  overflow: hidden;

  h3 {
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }

  .report-body {
    height: 80px;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

.managr {
  position: absolute;
  bottom: 16px;
  right: 16px;
  background: transparent;
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