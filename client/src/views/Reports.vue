<template>
  <div class="reports">
    <Modal class="bio-modal med-modal" v-if="threadModalOpen">
      <div class="bio-container med-container">
        <div class="header-alt">
          <h2 style="margin: 12px 0">{{ reportThread.title }}</h2>
          <!-- <p>shoudl something be here </p> -->
        </div>

        <div
          class="col"
          style="margin-top: 16px; margin-bottom: 24px; min-height: 120px; width: 100%"
        >
          <div class="row" style="margin-bottom: 8px">
            <label style="font-size: 16px; margin-right: 4px" class="bold">Thread:</label>
            <p>{{ reportThread.thread.title }}</p>
          </div>

          <div class="row">
            <label style="font-size: 16px; margin-right: 4px" class="bold" for="outlet"
              >Brand:</label
            >
            <p>{{ reportThread.brand }}</p>
          </div>

          <div style="margin-top: 8px" class="col">
            <div v-if="reportThread.thread.meta_data.type !== 'social'" class="row">
              <label class="bold" for=""> {{ urlCount }} URLs added:</label>
              <p style="margin-left: 4px">You can add or remove from the box below</p>
            </div>

            <div v-else class="row">
              <label style="font-size: 16px; margin-right: 4px" class="bold" for="">Content:</label>
              <p>{{ urlCount }} social media clips</p>
            </div>

            <textarea
              v-if="reportThread.thread.meta_data.type !== 'social'"
              style="
                width: 100%;
                border: 1px solid rgba(0, 0, 0, 0.1) !important;
                padding: 12px;
                margin-top: 8px;
              "
              :rows="5"
              id="search-input"
              class="area-input"
              autocomplete="off"
              :placeholder="urlPlaceholder"
              v-model="reportUrls"
              v-autoresize
              :disabled="urlsSet"
              @input="handleInput"
            />
          </div>
        </div>

        <div style="margin: 8px 0">
          <label style="font-size: 16px" class="bold">Report banner:</label>
          <div style="margin-top: 8px" class="file-input-wrapper">
            <label class="file-input-label">
              <input type="file" @change="uploadImage" class="file-input" />
              <span style="margin-right: 4px" class="secondary-button">
                <img
                  v-if="loading && !fileName"
                  style="margin-right: 4px"
                  class="invert rotation"
                  src="@/assets/images/loading.svg"
                  height="14px"
                  alt=""
                />
                Upload Banner
              </span>
            </label>
            <p style="margin-left: 8px" class="file-name">
              {{ fileName ? fileName : 'No file selected' }}
            </p>

            <img
              v-if="fileName"
              style="margin-left: 8px"
              :src="uploadedImageUrl"
              height="40px"
              alt=""
            />
          </div>
        </div>

        <footer>
          <div></div>
          <div class="row">
            <!-- <button class="secondary-button" @click="threadModalOpen = false">Cancel</button> -->
            <button :disabled="!fileName || loading" @click="getReportClips" class="primary-button">
              {{ !loading ? 'Run Report' : loadingText }}

              <img
                style="margin: 0 0 0 6px; filter: none"
                v-if="loading"
                class="rotation"
                src="@/assets/images/loading.svg"
                height="14px"
                alt=""
              />
            </button>
          </div>
        </footer>
      </div>
    </Modal>
    <div v-if="creating">
      <div class="chat-window">
        <div class="chat-window__header">
          <p>Coverage Report</p>
        </div>

        <div ref="chatWindow" class="chat-window__body">
          <div class="space-between">
            <div></div>
            <div class="chat-window__chat-bubble row">
              <img src="@/assets/images/profile.svg" height="12px" alt="" />
              <p>Create a report based on a Thread</p>
            </div>
          </div>

          <div>
            <div class="big-chat-bubble">
              <div class="row">
                <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
                <p class="regular-font" v-typed="nameText"></p>
              </div>
            </div>
          </div>

          <div
            @mouseenter="hoveringName = true"
            @mouseleave="hoveringName = false"
            v-if="reportName"
            class="space-between"
          >
            <div></div>

            <div style="position: relative" class="chat-window__chat-bubble row">
              <div
                @click="toggleEditName"
                v-if="!editingName && hoveringName"
                style="cursor: pointer"
                class="abs-img-left"
              >
                <img src="@/assets/images/pencil.svg" height="14px" alt="" />
              </div>

              <div
                @click="updateName"
                v-else-if="hoveringName"
                style="cursor: pointer"
                class="abs-img-left"
              >
                <img src="@/assets/images/close.svg" height="18px" alt="" />
              </div>

              <div v-if="!editingName" class="row">
                <img src="@/assets/images/profile.svg" height="12px" alt="" />
                <p>{{ reportName }}</p>
              </div>

              <div v-else style="opacity: 1; margin: 0; cursor: text" class="input-container-small">
                <input
                  style="border: none; outline: none; padding: 10px 8px 10px 0px; width: 100%"
                  type="text"
                  @keyup.enter="updateName"
                  v-model="reportName"
                  placeholder="Brand name..."
                />

                <div
                  class="img-container-stay-small-txt"
                  v-if="reportName"
                  @click="updateName"
                  style="margin-right: 12px; padding: 1px 6px 2px 6px"
                >
                  Save
                  <img src="@/assets/images/arrow-right.svg" class="pointer" height="10px" alt="" />
                </div>

                <img
                  v-else
                  style="filter: invert(40%); margin-right: 20px"
                  src="@/assets/images/edit.svg"
                  height="14px"
                  alt=""
                />
              </div>
            </div>
          </div>

          <div v-if="reportName">
            <div class="big-chat-bubble">
              <div class="row">
                <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
                <p class="regular-font" v-typed="brandText"></p>
              </div>
            </div>
          </div>

          <div
            @mouseenter="hovering = true"
            @mouseleave="hovering = false"
            v-if="brand"
            class="space-between"
          >
            <div></div>

            <div style="position: relative" class="chat-window__chat-bubble">
              <div
                @click="toggleEditBrand"
                v-if="!editingBrand && hovering"
                style="cursor: pointer"
                class="abs-img-left"
              >
                <img src="@/assets/images/pencil.svg" height="14px" alt="" />
              </div>

              <div
                @click="updateBrand"
                v-else-if="hovering"
                style="cursor: pointer"
                class="abs-img-left"
              >
                <img src="@/assets/images/close.svg" height="18px" alt="" />
              </div>

              <div class="row" v-if="!editingBrand">
                <img src="@/assets/images/profile.svg" height="12px" alt="" />
                <p>{{ brand }}</p>
              </div>

              <div v-else style="opacity: 1; margin: 0; cursor: text" class="input-container-small">
                <input
                  style="border: none; outline: none; padding: 10px 8px 10px 0px; width: 100%"
                  type="text"
                  @keyup.enter="updateBrand"
                  v-model="brand"
                  placeholder="Brand name..."
                />

                <div
                  class="img-container-stay-small-txt"
                  v-if="brand"
                  @click="updateBrand"
                  style="margin-right: 12px; padding: 1px 6px 2px 6px"
                >
                  Save
                  <img src="@/assets/images/arrow-right.svg" class="pointer" height="10px" alt="" />
                </div>

                <img
                  v-else
                  style="filter: invert(40%); margin-right: 20px"
                  src="@/assets/images/edit.svg"
                  height="14px"
                  alt=""
                />
              </div>
            </div>
          </div>

          <div v-if="brand">
            <div style="width: fit-content" class="big-chat-bubble">
              <div class="row">
                <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
                <p class="regular-font" v-typed="uploadText"></p>
              </div>

              <div style="margin: 0 0 8px 14px" class="row">
                <div class="file-input-wrapper">
                  <label class="file-input-label">
                    <input type="file" @change="uploadImage" class="file-input" />
                    <span style="margin-right: 4px" class="secondary-button">
                      <img
                        v-if="loading"
                        style="margin-right: 4px"
                        class="invert rotation"
                        src="@/assets/images/loading.svg"
                        height="14px"
                        alt=""
                      />
                      Upload Banner
                    </span>
                  </label>
                  <p style="margin-left: 8px" class="file-name">
                    {{ fileName ? fileName : 'No file selected' }}
                  </p>

                  <img
                    v-if="fileName"
                    style="margin-left: 8px"
                    :src="uploadedImageUrl"
                    height="40px"
                    alt=""
                  />
                </div>
              </div>
            </div>
          </div>

          <div v-if="fileName" class="space-between">
            <div></div>
            <div class="chat-window__chat-bubble row">
              <img src="@/assets/images/profile.svg" height="12px" alt="" />
              <p>{{ fileName }} uploaded</p>
            </div>
          </div>

          <div v-if="fileName">
            <div style="width: 80%" class="big-chat-bubble">
              <div class="row">
                <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
                <p class="regular-font" v-typed="urlText"></p>
              </div>
              <div style="margin: 0 0 8px 14px">
                <div class="relative">
                  <div
                    @click.stop="toggleSource"
                    class="drop-header-alt"
                    style="background-color: #fafafa; box-shadow: 1px 2px 6px rgba(0, 0, 0, 0.1)"
                  >
                    <p style="font-size: 15px !important" class="mobile-text-hide">
                      {{ sourceType ? sourceType : 'Select source' }}
                    </p>
                    <img
                      v-if="!showSource"
                      src="@/assets/images/arrowDropUp.svg"
                      height="15px"
                      alt=""
                    />
                    <img
                      v-else
                      class="rotate-img"
                      src="@/assets/images/arrowDropUp.svg"
                      height="15px"
                      alt=""
                    />
                  </div>

                  <div
                    v-show="showSource"
                    v-outside-click="hideSource"
                    class="container-left-below"
                  >
                    <section>
                      <h3>Select a source</h3>
                    </section>

                    <div>
                      <p
                        v-for="(source, i) in sources"
                        :key="i"
                        @click="selectSource(source.value)"
                      >
                        {{ source.name }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="sourceType" class="space-between">
            <div></div>
            <div class="chat-window__chat-bubble row">
              <img src="@/assets/images/profile.svg" height="12px" alt="" />
              <p>{{ sourceType === 'url' ? 'Upload URLs' : 'Saved Thread' }}</p>
            </div>
          </div>

          <div v-if="sourceType">
            <div style="width: 80%" class="big-chat-bubble">
              <div class="row fadein">
                <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
                <p v-if="sourceType === 'url'" class="regular-font">{{ fileText }}</p>
                <p v-else-if="sourceType === 'saved'" class="regular-font">{{ savedText }}</p>
                <p v-else-if="sourceType === 'both'" class="regular-font">{{ savedText }}</p>
              </div>

              <div
                v-if="sourceType === 'saved' || sourceType === 'both'"
                style="margin: 0 0 8px 20px"
              >
                <!-- <p class="thin-font">We will gather news coverage based on your selected search</p> -->

                <div style="margin: 12px 0" class="relative">
                  <div
                    @click.stop="toggleSearches"
                    class="drop-header-alt"
                    style="background-color: #fafafa; box-shadow: 1px 2px 6px rgba(0, 0, 0, 0.1)"
                  >
                    <p style="font-size: 15px !important" class="mobile-text-hide">
                      {{ selectedSearch ? selectedSearch.title : 'Select a thread' }}
                    </p>

                    <img
                      v-if="loadingClips"
                      style="margin-right: 4px"
                      class="rotation"
                      src="@/assets/images/loading.svg"
                      height="14px"
                      alt=""
                    />

                    <img
                      v-if="!showSearches && !loadingClips"
                      src="@/assets/images/arrowDropUp.svg"
                      height="15px"
                      alt=""
                    />
                    <img
                      v-else-if="showSearches && !loadingClips"
                      class="rotate-img"
                      src="@/assets/images/arrowDropUp.svg"
                      height="15px"
                      alt=""
                    />
                  </div>

                  <div
                    v-show="showSearches"
                    v-outside-click="hideSearches"
                    class="container-left-below"
                  >
                    <section>
                      <h3>Select a thread</h3>
                    </section>

                    <div v-if="savedThreads.length">
                      <p
                        v-for="(search, i) in savedThreads"
                        :key="i"
                        @click="selectSearch(search)"
                        class="row"
                      >
                        <img
                          v-if="search.meta_data.type === 'news'"
                          src="@/assets/images/globe.svg"
                          height="13px"
                          alt=""
                          style="margin-right: 10px; filter: invert(40%)"
                        />
                        <img
                          style="margin-right: 10px; filter: invert(40%)"
                          v-else
                          src="@/assets/images/thumb.svg"
                          height="13px"
                          alt=""
                        />
                        {{ search.title }}
                      </p>
                    </div>
                    <div v-else>You dont have any saved threads...</div>
                  </div>
                </div>
              </div>

              <div
                v-if="sourceType === 'url' || (sourceType === 'both' && selectedSearch)"
                style="margin: 0 0 8px 14px"
              >
                <p style="margin-top: 24px" v-if="sourceType === 'both'" class="">
                  {{ urlCount }} URLs added from the saved thread. Add additional URLs below,
                  separated by commas or new lines.
                </p>

                <p v-else class="thin-font">
                  Paste up to 200 URLs. Each on a new line or separated by commas.
                </p>

                <textarea
                  style="
                    width: 100%;
                    border: 1px solid rgba(0, 0, 0, 0.1) !important;
                    padding: 12px;
                  "
                  :rows="5"
                  id="search-input"
                  class="area-input"
                  autocomplete="off"
                  :placeholder="urlPlaceholder"
                  v-model="reportUrls"
                  v-autoresize
                  :disabled="urlsSet"
                  @input="handleInput"
                />
                <div style="margin-top: 12px" class="flex-end">
                  <button
                    @click="setUrls"
                    :disabled="!reportUrls || urlsSet"
                    class="primary-button"
                  >
                    Continue
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div v-if="urlsSet" class="space-between">
            <div></div>
            <div class="chat-window__chat-bubble row">
              <img src="@/assets/images/profile.svg" height="12px" alt="" />
              <p>
                {{ urlCount }}
                {{ selectedSearch.meta_data.type === 'news' ? 'URLs uploaded' : 'Posts uploaded' }}
              </p>
            </div>
          </div>

          <div v-if="urlsSet">
            <div class="big-chat-bubble">
              <div class="row">
                <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
                <p class="regular-font" v-typed="lastInstructions"></p>
              </div>

              <div style="margin: 0 0 8px 8px">
                <button :disabled="loading" @click="getReportClips" class="primary-button">
                  Run report
                </button>
              </div>
            </div>
          </div>

          <div v-if="loading" class="space-between">
            <div class="chat-window__chat-bubble row">
              <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
              <p style="margin-right: 6px">{{ loadingText }}</p>
              <img class="rotation" src="@/assets/images/loading.svg" height="14px" alt="" />
            </div>
            <div></div>
          </div>
        </div>

        <div class="chat-window__footer">
          <div class="large-input-container">
            <div style="border-radius: 28px" class="input-container-gray">
              <section>
                <textarea
                  ref="textarea"
                  style="width: 100%"
                  :rows="1"
                  id="search-input"
                  class="area-input"
                  autocomplete="off"
                  placeholder="Message ManagrAI..."
                  v-model="searchText"
                  v-autoresize
                  :disabled="loading || (!!brand && !!reportName)"
                  @keyup.enter="generateReportSearch($event)"
                />

                <div
                  v-if="searchText"
                  @click="generateReportSearch($event)"
                  class="left-margin pointer lite-bg img-container-stay-alt"
                  style="margin-right: 16px"
                >
                  <img
                    style="margin: 0"
                    src="@/assets/images/paper-plane-full.svg"
                    height="12px"
                    alt=""
                  />
                </div>
              </section>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="fadein" v-else>
      <div class="chat-window">
        <div class="chat-window__header">
          <p class="thin-font">
            <span class="bold-font">{{ brand }}</span> Coverage Report
          </p>
          <div :class="{ opaque: editSummary }" class="row">
            <button @click="clearData" class="secondary-button">Back</button>
            <button
              v-if="!reportLink"
              :disabled="reportLoading || loading"
              :loading="reportLoading"
              @click="createReport"
              class="primary-button"
            >
              Save
              <img
                v-if="reportLoading"
                style="margin-left: 6px"
                class="rotation invert"
                src="@/assets/images/loading.svg"
                height="14px"
                alt=""
              />
            </button>

            <button :disabled="loading" v-else @click="viewReport" class="primary-button">
              View Report
            </button>

            <!-- <img src="@/assets/images/disk.svg" height="14px" alt="" /> -->
          </div>
        </div>

        <div class="chat-window__body">
          <div ref="topDivider" v-if="view === 'home'">
            <div :class="{ opaque: loading }" style="padding-top: 20px" class="container fadein">
              <div>
                <img :src="uploadedImageUrl" class="photo-header" />
              </div>
              <div style="margin-top: 12px" v-if="editSummary" class="space-between fadein">
                <div></div>
                <button @click="closeSummaryEdit" class="primary-button turq-bg">
                  Update Report
                </button>
              </div>
              <pre
                ref="editablePre"
                :class="{ text: editSummary }"
                v-html="summary"
                @input="updateSummary"
                :contenteditable="editSummary"
                class="pre-text"
              ></pre>
            </div>
          </div>

          <div ref="topDivider" class="fadein" v-else-if="view === 'charts'">
            <div class="container fadein">
              <div class="space-between bottom-margin">
                <div class="col">
                  <p class="bold-font medium-txt">Total coverage</p>
                  <small>Number of news clips in this report</small>
                </div>

                <p class="bold-font">{{ clips.length }}</p>
              </div>

              <div class="space-between bottom-margin">
                <div class="col">
                  <p class="bold-font medium-txt">
                    {{
                      selectedSearch.meta_data.type === 'news'
                        ? 'Unique visitors'
                        : 'Potential Reach'
                    }}
                  </p>
                  <small>The potential audience reached by your media coverage</small>
                </div>

                <div class="row">
                  <img
                    style="margin-right: 8px"
                    src="@/assets/images/users.svg"
                    height="16px"
                    alt=""
                  />
                  <p class="bold-font">{{ formatNumber(totalVisits) }}</p>
                </div>
              </div>

              <div class="space-between">
                <div class="col">
                  <p class="bold-font medium-txt">
                    {{ selectedSearch.meta_data.type === 'news' ? 'Total shares' : 'Total likes' }}
                  </p>
                  <small>Number of times content was shared on social media</small>
                </div>

                <section v-if="selectedSearch.meta_data.type === 'news'" class="row img-mar">
                  <div style="margin-right: 12px" class="row">
                    <img src="@/assets/images/facebook.png" height="20px" alt="" />
                    <p class="bold-font">{{ socialTotals.totalFacebookLikes }}</p>
                  </div>
                  <div style="margin-right: 12px" class="row">
                    <img src="@/assets/images/twitter-x.svg" height="16px" alt="" />
                    <p class="bold-font">{{ socialTotals.totalTwitterLikes }}</p>
                  </div>
                  <div style="margin-right: 12px" class="row">
                    <img src="@/assets/images/reddit.svg" height="20px" alt="" />
                    <p class="bold-font">{{ socialTotals.totalRedditLikes }}</p>
                  </div>
                  <div class="row">
                    <img src="@/assets/images/pinterest.png" height="20px" alt="" />
                    <p class="bold-font">{{ socialTotals.totalPinterestLikes }}</p>
                  </div>
                </section>

                <section v-else class="row img-mar">
                  <div style="margin-right: 12px" class="row">
                    <img src="@/assets/images/twitter-x.svg" height="15px" alt="" />
                    <p class="bold-font">{{ formatNumber(socialTotals.totalTwitterLikes) }}</p>
                  </div>
                  <div style="margin-right: 12px" class="row">
                    <img src="@/assets/images/youtube.png" height="16px" alt="" />
                    <p class="bold-font">{{ formatNumber(socialTotals.totalYoutubeLikes) }}</p>
                  </div>
                  <div style="margin-right: 12px" class="row">
                    <img src="@/assets/images/bluesky.png" height="20px" alt="" />
                    <p class="bold-font">{{ formatNumber(socialTotals.totalBlueskyLikes) }}</p>
                  </div>
                </section>
              </div>
            </div>

            <div class="container">
              <div class="col bottom-margin">
                <p class="bold-font medium-txt">Media exposure over time</p>
                <small>Number of media clips along with the potential reach</small>
              </div>
              <ReportLineChart
                :volume="clipChartData.clipCountList"
                :reach="clipChartData.usersList"
                :dates="clipChartData.dateList"
              />
            </div>
          </div>
          <div ref="topDivider" class="fadein" v-else-if="view === 'starred'">
            <div class="fadein" v-if="!starredArticles.length">
              <p class="row">
                Your starred articles<span style="margin: 0 6px"
                  ><img src="@/assets/images/newspaper.svg" height="14px" alt=""
                /></span>
                will appear here
              </p>
            </div>

            <div v-else>
              <div v-for="(article, i) in starredArticles" :key="i" class="container fadein">
                <div
                  style="position: relative"
                  :class="selectedSearch.meta_data.type === 'news' ? container__top : ''"
                >
                  <div class="abs-top-right">
                    <img
                      @click="starArticle(article)"
                      class="blue-filter fadein"
                      style="cursor: pointer"
                      src="@/assets/images/fullstar.svg"
                      height="16px"
                      alt=""
                    />
                  </div>
                  <div style="margin-bottom: 12px">
                    <img
                      v-if="selectedSearch.meta_data.type === 'news'"
                      @error="onImageError($event)"
                      :src="article.image"
                      class="photo-header-small"
                    />

                    <img
                      v-else-if="article.type === 'twitter'"
                      @error="onImageError($event)"
                      :src="article.user.profile_image_url.replace('_normal', '')"
                      class="photo-header-small"
                      loading="lazy"
                    />

                    <img
                      v-else
                      @error="onImageError($event)"
                      :src="
                        article.type === 'youtube'
                          ? article.image_url.replace('default', 'hqdefault')
                          : article.image_url
                          ? article.image_url
                          : blueskyPlaceholder
                      "
                      class="photo-header-small"
                    />
                  </div>

                  <div
                    v-if="selectedSearch.meta_data.type === 'news'"
                    class="space-between no-letter-margin"
                  >
                    <div class="col">
                      <p class="bold-font">
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

                  <div v-else class="space-between no-letter-margin">
                    <div class="col">
                      <!-- <p class="bold-font row">
                        <img
                          v-if="article.type === 'twitter'"
                          src="@/assets/images/twitter-x.svg"
                          height="12px"
                          alt=""
                          style="margin-right: 8px"
                        />
                        <img
                          v-else-if="article.type === 'bluesky'"
                          src="@/assets/images/bluesky.png"
                          height="14px"
                          alt=""
                          style="margin-right: 8px"
                        />
                        <img
                          v-else
                          src="@/assets/images/youtube.png"
                          height="12px"
                          alt=""
                          style="margin-right: 8px"
                        />

                        {{ article.type }}
                      </p> -->

                      <div style="margin-top: 8px" class="row">
                        <img
                          v-if="article.type === 'twitter'"
                          src="@/assets/images/twitter-x.svg"
                          height="12px"
                          alt=""
                          style="margin-right: 8px"
                        />
                        <img
                          v-else-if="article.type === 'bluesky'"
                          src="@/assets/images/bluesky.png"
                          height="14px"
                          alt=""
                          style="margin-right: 8px"
                        />
                        <img
                          v-else
                          src="@/assets/images/youtube.png"
                          height="12px"
                          alt=""
                          style="margin-right: 8px"
                        />
                        <p>{{ article.type === 'twitter' ? article.user.name : article.author }}</p>
                      </div>
                    </div>
                    <small>{{ getTimeDifferenceInMinutes(article.created_at) }}</small>
                  </div>

                  <div>
                    <div
                      v-if="selectedSearch.meta_data.type === 'news'"
                      class="elipsis-text"
                      style="margin: 20px 0"
                    >
                      <a :href="article.url" target="_blank" class="bold-txt">
                        {{ article.description }}</a
                      >
                    </div>

                    <div v-else class="elipsis-text" style="margin: 20px 0">
                      <p
                        @click="openTweet(article.user.username, article.id)"
                        v-if="article.type === 'twitter'"
                        class="bold-txt"
                      >
                        {{ article.text }}
                      </p>

                      <a v-else :href="article.url" target="_blank" class="bold-txt">
                        {{ article.text }}</a
                      >
                    </div>
                  </div>

                  <div
                    v-if="selectedSearch.meta_data.type === 'news'"
                    class="space-between bottom-margin-m"
                  >
                    <div class="row img-mar">
                      <img src="@/assets/images/users.svg" height="14px" alt="" />
                      <p class="bold-font">
                        {{ article.traffic ? formatNumber(article.traffic.users) : 0 }}
                      </p>
                    </div>

                    <section class="row img-mar">
                      <div style="margin-right: 12px" class="row">
                        <img src="@/assets/images/facebook.png" height="14px" alt="" />
                        <p class="bold-font">
                          {{
                            formatNumber(
                              socialData[article.url] && socialData[article.url][0]
                                ? socialData[article.url][0]['total_facebook_shares']
                                  ? socialData[article.url][0]['total_facebook_shares']
                                  : 0
                                : 0,
                            )
                          }}
                        </p>
                      </div>

                      <div style="margin-right: 12px" class="row">
                        <img
                          style="margin-right: 4px"
                          src="@/assets/images/twitter-x.svg"
                          height="14px"
                          alt=""
                        />
                        <p class="bold-font">
                          {{
                            formatNumber(
                              socialData[article.url] && socialData[article.url][0]
                                ? socialData[article.url][0]['twitter_shares']
                                  ? socialData[article.url][0]['twitter_shares']
                                  : 0
                                : 0,
                            )
                          }}
                        </p>
                      </div>

                      <div style="margin-right: 12px" class="row">
                        <img src="@/assets/images/reddit.svg" height="14px" alt="" />
                        <p class="bold-font">
                          {{
                            formatNumber(
                              socialData[article.url] && socialData[article.url][0]
                                ? socialData[article.url][0]['total_reddit_engagements']
                                  ? socialData[article.url][0]['total_reddit_engagements']
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
                        <p class="bold-font">
                          {{
                            formatNumber(
                              socialData[article.url] && socialData[article.url][0]
                                ? socialData[article.url][0]['pinterest_shares']
                                  ? socialData[article.url][0]['pinterest_shares']
                                  : 0
                                : 0,
                            )
                          }}
                        </p>
                      </div>
                    </section>
                  </div>

                  <div v-else class="space-between bottom-margin-m">
                    <div class="row img-mar">
                      <img src="@/assets/images/users.svg" height="14px" alt="" />
                      <p v-if="article.type === 'twitter'" class="bold-font">
                        {{
                          article.user.public_metrics.followers_count
                            ? formatNumber(article.user.public_metrics.followers_count)
                            : 0
                        }}
                      </p>

                      <p v-else-if="article.type === 'youtube'" class="bold-font">
                        {{ formatNumber(article.stats.viewCount) }}
                      </p>

                      <p v-else class="bold-font">
                        {{
                          formatNumber(
                            article.stats.likes +
                              article.stats.quotes +
                              article.stats.replies +
                              article.stats.reposts,
                          )
                        }}
                      </p>
                    </div>

                    <section class="row img-mar">
                      <div style="margin-right: 12px" class="row">
                        <img src="@/assets/images/heart.svg" height="14px" alt="" />
                        <p v-if="article.type === 'twitter'" class="bold-font">
                          {{ formatNumber(article.user.public_metrics.like_count) }}
                        </p>

                        <p v-else-if="article.type === 'bluesky'" class="bold-font">
                          {{ formatNumber(article.stats.likes) }}
                        </p>

                        <p v-else class="bold-font">
                          {{ formatNumber(article.stats.likeCount) }}
                        </p>
                      </div>

                      <div v-if="article.type === 'bluesky'" style="margin-right: 12px" class="row">
                        <img
                          style="margin-right: 4px"
                          src="@/assets/images/commentAlt.svg"
                          height="14px"
                          alt=""
                        />
                        <p class="bold-font">
                          {{ formatNumber(article.stats.replies) }}
                        </p>
                      </div>

                      <div v-if="article.type === 'bluesky'" style="margin-right: 12px" class="row">
                        <img
                          style="margin-right: 4px"
                          src="@/assets/images/arrows-retweet.svg"
                          height="14px"
                          alt=""
                        />
                        <p class="bold-font">
                          {{ formatNumber(article.stats.reposts) }}
                        </p>
                      </div>

                      <div v-if="article.type === 'youtube'" style="margin-right: 12px" class="row">
                        <img
                          style="margin-right: 4px"
                          src="@/assets/images/commentAlt.svg"
                          height="14px"
                          alt=""
                        />
                        <p class="bold-font">
                          {{ formatNumber(article.stats.commentCount) }}
                        </p>
                      </div>
                    </section>
                  </div>
                </div>

                <div v-if="article.summary" class="report-body">
                  <div style="margin-top: 12px">
                    <pre v-html="article.summary" class="pre-text"></pre>
                  </div>
                </div>

                <div v-else-if="selectedSearch.meta_data.type === 'news'" class="report-body">
                  <div class="space-between" style="margin-top: 12px">
                    <div></div>
                    <button
                      :disabled="summaryLoading || loading"
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
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div ref="topDivider" class="fadein" v-else-if="view === 'articles'">
            <div class="container fadein">
              <div v-for="(article, i) in clips" :key="i" class="article">
                <div class="space-between">
                  <p v-if="selectedSearch.meta_data.type === 'news'" class="bold-font">
                    {{ article.traffic ? removeDomain(article.traffic.target) : 'unknown' }}
                  </p>

                  <p v-else class="bold-font row">
                    <img
                      v-if="article.type === 'twitter'"
                      src="@/assets/images/twitter-x.svg"
                      height="12px"
                      alt=""
                      style="margin-right: 8px"
                    />
                    <img
                      v-else-if="article.type === 'bluesky'"
                      src="@/assets/images/bluesky.png"
                      height="14px"
                      alt=""
                      style="margin-right: 8px"
                    />
                    <img
                      v-else
                      src="@/assets/images/youtube.png"
                      height="12px"
                      alt=""
                      style="margin-right: 8px"
                    />

                    {{
                      article.author
                        ? article.author
                        : article.type === 'twitter'
                        ? article.user.name
                        : 'Unknown'
                    }}
                  </p>

                  <img
                    v-if="!starredArticles.includes(article)"
                    @click="starArticle(article)"
                    style="cursor: pointer"
                    class="fadein"
                    src="@/assets/images/star.svg"
                    height="16px"
                    alt=""
                  />
                  <img
                    v-else
                    @click="starArticle(article)"
                    class="blue-filter fadein"
                    style="cursor: pointer"
                    src="@/assets/images/fullstar.svg"
                    height="16px"
                    alt=""
                  />
                </div>

                <div v-if="selectedSearch.meta_data.type === 'news'" class="space-between-bottom">
                  <div class="article-body">
                    <div style="margin: 20px 0">
                      <a :href="article.url" target="_blank" class="bold-txt elipsis-text">
                        {{ article.title }}</a
                      >
                    </div>

                    <p class="report-body">
                      {{ article.description }}
                    </p>
                  </div>

                  <img
                    @error="onImageError($event)"
                    :src="article.image"
                    class="photo-header-alt"
                  />
                </div>

                <div v-else class="space-between-bottom">
                  <div class="article-body">
                    <div v-if="article.type !== 'twitter'" style="margin: 20px 0">
                      <a :href="article.url" target="_blank" class="bold-txt elipsis-text">
                        {{ article.title ? article.title : article.text }}</a
                      >
                    </div>

                    <div
                      @click="openTweet(article.user.username, article.id)"
                      v-else
                      style="margin: 20px 0"
                    >
                      <p class="bold-txt elipsis-text">
                        {{ article.title ? article.title : article.text }}
                      </p>
                    </div>

                    <p class="report-body">
                      {{ article.text }}
                    </p>
                  </div>

                  <img
                    v-if="article.type === 'twitter'"
                    @error="onImageError($event)"
                    :src="article.user.profile_image_url.replace('_normal', '')"
                    class="photo-header-alt"
                  />

                  <img
                    v-else
                    @error="onImageError($event)"
                    :src="
                      article.type === 'youtube'
                        ? article.image_url.replace('default', 'hqdefault')
                        : article.image_url
                        ? article.image_url
                        : blueskyPlaceholder
                    "
                    class="photo-header-alt"
                  />
                </div>

                <div
                  v-if="selectedSearch.meta_data.type === 'news'"
                  style="margin-top: 12px"
                  class="space-between bottom-border"
                >
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
                      <p class="bold-font">
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
                      <p class="bold-font">
                        {{
                          formatNumber(
                            socialData[article.url] && socialData[article.url][0]
                              ? socialData[article.url][0]['total_facebook_shares']
                                ? socialData[article.url][0]['total_facebook_shares']
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
                      <p class="bold-font">
                        {{
                          formatNumber(
                            socialData[article.url] && socialData[article.url][0]
                              ? socialData[article.url][0]['twitter_shares']
                                ? socialData[article.url][0]['twitter_shares']
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
                      <p class="bold-font">
                        {{
                          formatNumber(
                            socialData[article.url] && socialData[article.url][0]
                              ? socialData[article.url][0]['total_reddit_engagements']
                                ? socialData[article.url][0]['total_reddit_engagements']
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
                      <p class="bold-font">
                        {{
                          formatNumber(
                            socialData[article.url] && socialData[article.url][0]
                              ? socialData[article.url][0]['pinterest_shares']
                                ? socialData[article.url][0]['pinterest_shares']
                                : 0
                              : 0,
                          )
                        }}
                      </p>
                    </div>
                  </div>
                </div>

                <div v-else style="margin-top: 12px" class="space-between bottom-border">
                  <div class="row report-body">
                    <div class="pill">
                      <img src="@/assets/images/profile.svg" height="12px" alt="" />
                      <p style="margin-right: 6px">
                        {{
                          article.author
                            ? article.author
                            : article.type === 'twitter'
                            ? article.user.name
                            : 'Unknown'
                        }}
                      </p>
                    </div>

                    <small>{{ getTimeDifferenceInMinutes(article.created_at) }}</small>
                  </div>

                  <div class="row small-text">
                    <div v-if="article.type === 'twitter'" style="margin-right: 16px" class="row">
                      <img
                        style="margin-right: 4px"
                        src="@/assets/images/users.svg"
                        height="14px"
                        alt=""
                      />
                      <p class="bold-font">
                        {{ formatNumber(article.user.public_metrics.followers_count) }}
                      </p>
                    </div>

                    <div v-if="article.type === 'twitter'" style="margin-right: 16px" class="row">
                      <img
                        style="margin-right: 4px"
                        src="@/assets/images/heart.svg"
                        height="14px"
                        alt=""
                      />
                      <p class="bold-font">
                        {{ formatNumber(article.user.public_metrics.like_count) }}
                      </p>
                    </div>

                    <div v-if="article.type === 'youtube'" style="margin-right: 16px" class="row">
                      <img
                        style="margin-right: 4px"
                        src="@/assets/images/users.svg"
                        height="14px"
                        alt=""
                      />
                      <p class="bold-font">
                        {{ formatNumber(article.stats.viewCount) }}
                      </p>
                    </div>

                    <div v-if="article.type === 'youtube'" style="margin-right: 16px" class="row">
                      <img
                        style="margin-right: 4px"
                        src="@/assets/images/heart.svg"
                        height="14px"
                        alt=""
                      />
                      <p class="bold-font">
                        {{ formatNumber(article.stats.likeCount) }}
                      </p>
                    </div>

                    <div v-if="article.type === 'youtube'" class="row">
                      <img
                        style="margin-right: 4px"
                        src="@/assets/images/commentAlt.svg"
                        height="14px"
                        alt=""
                      />
                      <p class="bold-font">
                        {{ formatNumber(article.stats.commentCount) }}
                      </p>
                    </div>

                    <div v-if="article.type === 'bluesky'" style="margin-right: 16px" class="row">
                      <img
                        style="margin-right: 4px"
                        src="@/assets/images/heart.svg"
                        height="14px"
                        alt=""
                      />
                      <p class="bold-font">
                        {{ formatNumber(article.stats.likes) }}
                      </p>
                    </div>

                    <div v-if="article.type === 'bluesky'" style="margin-right: 16px" class="row">
                      <img
                        style="margin-right: 4px"
                        src="@/assets/images/commentAlt.svg"
                        height="14px"
                        alt=""
                      />
                      <p class="bold-font">
                        {{ formatNumber(article.stats.replies) }}
                      </p>
                    </div>

                    <div v-if="article.type === 'bluesky'" class="row">
                      <img
                        style="margin-right: 4px"
                        src="@/assets/images/arrows-retweet.svg"
                        height="14px"
                        alt=""
                      />
                      <p class="bold-font">
                        {{ formatNumber(article.stats.reposts) }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <nav v-if="!creating" class="left-nav">
      <ul class="nav-links">
        <li @click="changeView('home')" class="nav-item s-wrapper">
          <div :class="{ active: view === 'home' }">
            <img src="@/assets/images/home.svg" height="16px" alt="" />
          </div>

          <section class="s-tooltip-right">Home</section>
        </li>

        <li @click="changeView('charts')" class="nav-item s-wrapper">
          <div :class="{ active: view === 'charts' }">
            <img src="@/assets/images/stats.svg" height="16px" alt="" />
          </div>
          <section class="s-tooltip-right">Traffic</section>
        </li>

        <li @click="changeView('starred')" class="nav-item s-wrapper">
          <div :class="{ active: view === 'starred' }">
            <img src="@/assets/images/star.svg" height="16px" alt="" />
          </div>
          <section class="s-tooltip-right">Starred</section>
        </li>

        <li @click="changeView('articles')" class="nav-item s-wrapper">
          <div :class="{ active: view === 'articles' }">
            <img src="@/assets/images/newspaper.svg" height="16px" alt="" />
          </div>
          <section class="s-tooltip-right">Articles</section>
        </li>
      </ul>
    </nav>

    <div v-if="!creating && view == 'home'">
      <div @click.stop="openPanel" :class="{ expanded: panelOpen }" class="floating-panel">
        <div
          v-outside-click="closePanel"
          class="fadein panel-options"
          v-show="panelOpen && !loading"
        >
          <div v-if="showingReportEdit" class="abs-top">
            <div class="space-between">
              <p class="bold-txt">Regenerate</p>
              <img
                style="cursor: pointer"
                @click="showingReportEdit = !showingReportEdit"
                src="@/assets/images/close.svg"
                height="20px"
                alt=""
              />
            </div>

            <div>
              <textarea
                style="
                  width: 100%;
                  border: 1px solid rgba(0, 0, 0, 0.1) !important;
                  padding: 12px;
                  min-height: 100px;
                "
                :rows="5"
                id="search-input"
                class="area-input"
                autocomplete="off"
                placeholder="provide additional instructions for a new summary..."
                v-model="reportInstructions"
                v-autoresize
                :disabled="loading"
              />
              <div class="space-between">
                <div></div>
                <button @click="rewriteContent(reportInstructions)" class="primary-button">
                  Regenerate

                  <img
                    v-if="loading"
                    style="margin-left: 6px"
                    class="rotation invert"
                    src="@/assets/images/loading.svg"
                    height="14px"
                    alt=""
                  />
                </button>
              </div>
            </div>
          </div>

          <div @click="editSummary = !editSummary" class="s-wrapper">
            <img src="@/assets/images/pencil.svg" height="18px" alt="" />
            <section class="s-tooltip-left">Edit</section>
          </div>
          <div @click="showingReportEdit = !showingReportEdit" class="s-wrapper">
            <img src="@/assets/images/refresh-pr.svg" height="18px" alt="" />
            <section class="s-tooltip-left">Regenerate</section>
          </div>
          <div class="s-wrapper" @click="rewriteContent(shortText)">
            <img src="@/assets/images/sortup.svg" height="18px" alt="" />
            <section class="s-tooltip-left">Make shorter</section>
          </div>
          <div @click="rewriteContent(longText)" class="s-wrapper">
            <img src="@/assets/images/sortdwn.svg" height="18px" alt="" />
            <section class="s-tooltip-left">Make longer</section>
          </div>
        </div>
        <img
          v-if="!loading"
          :class="{ opaque: panelOpen }"
          src="@/assets/images/wand.svg"
          height="20px"
          alt=""
        />
        <img v-else class="rotation" src="@/assets/images/loading.svg" height="20px" alt="" />
      </div>
    </div>
  </div>
</template>

<script>
import ReportLineChart from '@/components/ReportLineChart.vue'
import { Comms } from '@/services/comms'
import User from '@/services/users'

export default {
  name: 'Reports',
  components: {
    ReportLineChart,
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
  },
  data() {
    return {
      preparedSocial: null,
      loadingClips: false,
      useSearchUrls: false,
      showSearches: false,
      selectedSearch: null,
      showSource: false,
      sourceType: null,
      sources: [
        { name: 'Upload URLs', value: 'url' },
        { name: 'Saved Thread', value: 'saved' },
        { name: 'Both', value: 'both' },
      ],
      editSummary: false,
      shortText: 'The report is too long. Make it shorter',
      longText: "The report isn't long enough. Make it longer",
      showingReportEdit: false,
      preppedClips: [],
      reportInstructions: '',
      panelOpen: false,
      hoveringName: false,
      hovering: false,
      editingBrand: false,
      editingName: false,
      reportLink: null,
      mainImage: null,
      reportLoading: false,
      summaryLoading: false,
      loadingUrl: null,
      clipChartData: null,
      socialTotals: null,
      socialData: null,
      totalVisits: 0,
      starredArticles: [],
      logoPlaceholder: require('@/assets/images/iconlogo.png'),
      traffic: null,
      urlCount: 0,
      urls: [],
      clips: [],
      loadingText: 'Analyzing articles...',
      loadingTextAlt: 'Analyzing media coverage...',
      summary: '',
      view: 'home',
      creating: true,
      reportName: '',
      brandText: 'Next, tell us which brands are included in this report (e.g. Nike, Tesla, FSU)',
      nameText: 'Using the message bar below, provide a title for your report',
      loading: false,
      brand: '',
      searchText: '',
      uploadText: 'Upload banner image using JPEG, PNG, or SVG',
      fileName: '',
      allowedFormats: [
        'image/jpeg',
        'image/png',
        'image/svg+xml',
        // 'image/gif',
        // 'image/tiff',
        // 'image/bmp',
        // 'application/pdf',
      ],
      maxSize: 2 * 1024 * 1024,
      fileText: `Next, add news coverage links by pasting the URL's below.`,
      savedText: `Got it, pick one of your saved threads`,
      urlText: 'Where would you like us to pull the clips from ?',
      reportUrls: '',
      urlsSet: false,
      urlPlaceholder: `
www.techcrunch.com/article-1 
www.bloomberg.com/article-2
www.forbes.com/article-3
     `,
      lastInstructions: 'All set! We are now ready to run the report!',
      uploadedImageUrl: '',
      dateStart: null,
      dateEnd: null,
      blueskyPlaceholder: require('@/assets/images/bluesky.png'),
      threadModalOpen: false,
    }
  },
  watch: {
    editSummary(newVal) {
      console.log(newVal)
      if (newVal) {
        this.$nextTick(() => {
          this.$refs.editablePre.focus()
          this.panelOpen = false
        })
      }
    },
  },
  computed: {
    reportThread() {
      return this.$store.state.reportThread
    },
    reports() {
      return this.$store.state.allReports
    },
    savedThreads() {
      if (this.sourceType === 'both') {
        return this.$store.state.allThreads.filter(
          (thread) => thread.meta_data.type && thread.meta_data.type === 'news',
        )
      } else {
        return this.$store.state.allThreads.filter(
          (thread) =>
            thread.meta_data.type &&
            (thread.meta_data.type === 'news' || thread.meta_data.type === 'social'),
        )
      }
    },
    user() {
      return this.$store.state.user
    },
  },
  mounted() {
    if (this.$store.state.reportThread) {
      this.setReportClips()
      this.threadModalOpen = true
      // console.log(this.reportThread)
    }
  },
  beforeRouteLeave(to, from, next) {
    this.$store.dispatch('updateSharedObject', null)
    next()
  },
  created() {
    const today = new Date()
    const sevenDaysAgo = new Date(today)
    sevenDaysAgo.setDate(today.getDate() - 30)

    this.dateStart = sevenDaysAgo.toISOString().split('T')[0]
    this.dateEnd = today.toISOString().split('T')[0]
  },
  methods: {
    setReportClips() {
      this.selectedSearch = this.reportThread.thread
      this.reportName = this.reportThread.title
      this.brand = this.reportThread.brand

      console.log('REPORT THREAD IS HERE', this.reportThread)

      let articles = []
      let clips = []

      if (this.selectedSearch.meta_data.type !== 'social') {
        articles = this.selectedSearch.meta_data.filteredArticles
        this.urls = articles.map((art) => {
          return art.link
        })
      } else {
        articles = this.selectedSearch.meta_data.preparedTweets

        clips = this.selectedSearch.meta_data.tweets
        this.preparedSocial = articles

        this.urls = clips.map((clip) => {
          return clip.link
        })
      }

      let additionalClips = this.selectedSearch.meta_data.summaries
        ? this.selectedSearch.meta_data.summaries.map((summary) => summary.clips)
        : []

      articles = [articles, ...additionalClips].flat()
      clips = [clips, ...additionalClips].flat()

      if (this.selectedSearch.meta_data.type !== 'social') {
        this.reportUrls = articles.map((art) => {
          return art.link
        })
      } else {
        this.reportUrls = articles.map((art) => {
          return art.link
        })
        this.clips = clips
      }

      this.urlCount = this.reportUrls.length
      this.useSearchUrls = true
    },
    openTweet(username, id) {
      window.open(`https://twitter.com/${username}/status/${id}`, '_blank')
    },
    getClips() {
      this.loadingClips = true

      let articles = []
      let clips = []

      if (this.selectedSearch.meta_data.type !== 'social') {
        articles = this.selectedSearch.meta_data.filteredArticles
      } else {
        articles = this.selectedSearch.meta_data.preparedTweets
        clips = this.selectedSearch.meta_data.tweets
      }

      let additionalClips = this.selectedSearch.meta_data.summaries
        ? this.selectedSearch.meta_data.summaries.map((summary) => summary.clips)
        : []

      articles = [articles, ...additionalClips].flat()
      clips = [clips, ...additionalClips].flat()

      console.log('clips here', clips)

      if (this.sourceType !== 'both') {
        if (this.selectedSearch.meta_data.type !== 'social') {
          this.urls = articles.map((art) => {
            return art.link
          })
          this.urlCount = this.urls.length
          this.useSearchUrls = true
          this.setUrls()
        } else {
          this.urls = articles
          this.clips = clips
          this.urlCount = this.urls.length
          this.useSearchUrls = true
          this.setUrls()
        }
      } else {
        if (this.selectedSearch.meta_data.type !== 'social') {
          this.reportUrls = articles.map((art) => {
            return art.link
          })
        } else {
          this.reportUrls = articles
        }

        this.urlCount = this.reportUrls.length
        this.useSearchUrls = true
      }

      this.loadingClips = false
    },
    toggleSource() {
      this.showSource = true
    },
    hideSource() {
      this.showSource = false
    },
    selectSource(val) {
      this.sourceType = val
      this.hideSource()
      this.scrollToChatTop()
    },
    toggleSearches() {
      this.showSearches = true
    },
    hideSearches() {
      this.showSearches = false
    },
    selectSearch(val) {
      this.selectedSearch = val
      this.hideSearches()
      this.scrollToChatTop()
      this.getClips()
    },
    closeSummaryEdit() {
      this.editSummary = false
    },
    updateSummary() {
      let selection = window.getSelection()
      let range = selection.getRangeAt(0)

      // Save the caret position as a character offset
      let preText = this.$refs.editablePre.innerText
      let caretOffset = this.getCaretCharacterOffsetWithin(this.$refs.editablePre)

      // Update summary with innerHTML to preserve formatting
      this.summary = this.$refs.editablePre.innerHTML

      this.$nextTick(() => {
        // Restore caret position after updating
        this.setCaretPosition(this.$refs.editablePre, caretOffset)
      })
    },

    // Helper function to get caret character offset within a contenteditable element
    getCaretCharacterOffsetWithin(element) {
      let caretOffset = 0
      let selection = window.getSelection()
      if (selection.rangeCount > 0) {
        let range = selection.getRangeAt(0)
        let preCaretRange = range.cloneRange()
        preCaretRange.selectNodeContents(element)
        preCaretRange.setEnd(range.endContainer, range.endOffset)
        caretOffset = preCaretRange.toString().length
      }
      return caretOffset
    },

    // Helper function to set the caret position at a specific character offset
    setCaretPosition(element, offset) {
      let selection = window.getSelection()
      let range = document.createRange()
      let currentNode = element
      let currentOffset = 0

      // Traverse the child nodes to find the correct text node for the caret position
      function traverseNodes(node) {
        if (node.nodeType === 3) {
          // Text node
          if (currentOffset + node.length >= offset) {
            range.setStart(node, offset - currentOffset)
            return true
          } else {
            currentOffset += node.length
          }
        } else {
          for (let i = 0; i < node.childNodes.length; i++) {
            if (traverseNodes(node.childNodes[i])) return true
          }
        }
        return false
      }

      traverseNodes(element)

      // Set the caret to the calculated position
      selection.removeAllRanges()
      selection.addRange(range)
    },
    openPanel() {
      if (!this.loading) {
        this.panelOpen = true
      }
    },
    closePanel() {
      this.panelOpen = false
      this.showingReportEdit = false
    },
    refreshUser() {
      User.api
        .getUser(this.user.id)
        .then((user) => {
          this.$store.dispatch('updateUser', user)
          return user
        })
        .catch(() => {
          return null
        })
    },
    updateBrand() {
      this.editingBrand = false
    },
    toggleEditBrand() {
      this.editingBrand = true
    },
    updateName() {
      this.editingName = false
    },
    toggleEditName() {
      this.editingName = true
    },
    removeDomain(url) {
      const domainRegex = /\.(com|net|org|gov|edu|co|io|biz|info|us)$/i

      return url.replace(domainRegex, '')
    },
    clearData() {
      this.$router.go(0)
    },
    viewReport() {
      window.open(this.reports[0].share_url, '_blank')
    },
    async createReport() {
      let is_social
      if (this.selectedSearch.meta_data.type === 'news') {
        is_social = false
      } else {
        is_social = true
      }

      this.reportLoading = true
      let formData = new FormData()
      formData.append('title', this.reportName)
      formData.append('main_image', this.mainImage)
      formData.append('user', this.$store.state.user.id)
      formData.append(
        'meta_data',
        JSON.stringify({
          clips: this.clips,
          summary: this.summary,
          chartData: this.clipChartData,
          starredArticles: this.starredArticles,
          socialData: this.socialData,
          socialTotals: this.socialTotals,
          totalVisits: this.totalVisits,
          urlCount: this.urlCount,
          brand: this.brand,
          is_social: is_social,
        }),
      )
      try {
        await User.api.createReport(formData)
        this.refreshUser()
        this.getReports()
        this.$toast('Report Saved!', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        console.log(e)
        this.$toast('Error saving report', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.reportLoading = false
      }
    },
    getReports() {
      this.$store.dispatch('getReports')
      this.$nextTick(() => {
        this.reportLink = 'link'
      })
    },
    scrollToTopDivider() {
      setTimeout(() => {
        this.$refs.topDivider.scrollIntoView({ behavior: 'smooth' })
      }, 300)
    },
    async getArticleSummary(url, instructions = null, length = 1000) {
      let selectedClip = []

      selectedClip = this.starredArticles.filter((art) => art.url === url)[0]

      this.summaryLoading = true
      this.loadingUrl = url

      try {
        const response = await Comms.api.getArticleSummary({
          url: url,
          search: this.brand,
          instructions: instructions,
          length: length,
        })

        selectedClip['summary'] = response.summary
          .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
          .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')

        if (!this.starredArticles.length) {
          this.starredArticles = this.starredArticles.filter(
            (clip) => clip.title !== selectedClip.title,
          )
          this.starredArticles.unshift(selectedClip)
        } else {
          this.starredArticles = this.starredArticles.filter(
            (clip) => clip.title !== selectedClip.title,
          )
          this.starredArticles.unshift(selectedClip)
        }
        this.scrollToTopDivider()
      } catch (e) {
        console.log(e)
        this.$toast('Request blocked by article source', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.summaryLoading = false
        this.loadingUrl = null
      }
    },
    starArticle(art) {
      if (art.hasOwnProperty('type')) {
        const index = this.starredArticles.findIndex((a) => a.text === art.text)

        if (index === -1) {
          this.starredArticles = [...this.starredArticles, art]
        } else {
          this.starredArticles = this.starredArticles.filter((a) => a.text !== art.text)
        }
      } else {
        const index = this.starredArticles.findIndex((a) => a.url === art.url)

        if (index === -1) {
          this.starredArticles = [...this.starredArticles, art]
        } else {
          this.starredArticles = this.starredArticles.filter((a) => a.url !== art.url)
        }
      }
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
    formatNumber(number) {
      // Round the number up using Math.ceil to remove decimals
      const roundedNumber = Math.ceil(number)

      // Convert the number to a string and format it with commas
      return roundedNumber.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
    },
    onImageError(event) {
      event.target.src = this.logoPlaceholder
    },
    async rewriteContent(instructions) {
      this.loading = true
      this.panelOpen = false
      try {
        const res = await Comms.api.rewriteReport({
          content: this.summary,
          instructions: instructions,
          clips: this.preppedClips,
        })
        this.summary = res.summary
          .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
          .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')
          .replace(/^### (.*$)/gim, '<h3>$1</h3>')
          // Convert #### to <h4></h4>
          .replace(/^#### (.*$)/gim, '<h4>$1</h4>')
          // Convert ## to <h2></h2> (if needed)
          .replace(/^## (.*$)/gim, '<h2>$1</h2>')
          // Convert # to <h1></h1> (if needed)
          .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        this.showingReportEdit = false
        this.loading = false
        this.$toast('Report updated', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.reportInstructions = ''
      } catch (e) {
        console.error(e)
        this.loadingText = 'Analyzing articles...'
        this.loading = false
        this.urlsSet = false
        this.$toast('Error uploading clips, try again', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async getReportClips() {
      this.loadingText = 'Step 1/4: Analyzing articles...'
      this.loading = true
      this.scrollToChatTop()

      if (this.selectedSearch.meta_data.type === 'news') {
        try {
          const res = await Comms.api.getReportClips({
            urls: this.reportUrls.length ? this.reportUrls : this.urls,
          })
          this.clips = res
          this.getTrafficData()
        } catch (e) {
          console.error(e)
          this.loadingText = 'Analyzing articles...'
          this.loading = false
          this.urlsSet = false
          this.$toast('Error uploading clips, try again', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        }
      } else {
        this.loadingText = 'Step 1/3: Analyzing media coverage...'

        console.log('preparedSocial are here', this.preparedSocial)

        try {
          const res = await Comms.api.getReportSummary({
            clips: this.preparedSocial ? this.preparedSocial : this.urls,
            brand: this.brand,
            social: true,
          })
          this.summary = res.summary
            .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
            .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            // Convert #### to <h4></h4>
            .replace(/^#### (.*$)/gim, '<h4>$1</h4>')
            // Convert ## to <h2></h2> (if needed)
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            // Convert # to <h1></h1> (if needed)
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')

          this.analyzeVideos()
          // this.loading = false
          // this.creating = false
        } catch (e) {
          console.error(e)
          this.loadingText = 'Analyzing articles...'
          this.loading = false
          this.urlsSet = false
          this.$toast('Error uploading clips, try again', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        }
      }
    },

    async analyzeVideos() {
      this.loadingText = 'Step 2/3: Gathering stats...'
      let ytClips = this.clips.filter((clip) => clip.type === 'youtube')

      for (let i = 0; i < ytClips.length; i++) {
        try {
          const res = await Comms.api.analyzeVideo({
            video_id: ytClips[i].id,
          })

          ytClips[i].stats = res

          const clipIndex = this.clips.findIndex((clip) => clip.id === ytClips[i].id)
          if (clipIndex !== -1) {
            this.clips[clipIndex] = ytClips[i]
          }
        } catch (e) {
          console.error('Error analyzing video:', e)
        }
      }

      this.combineSocialStats()
    },
    combineSocialStats() {
      this.loadingText = 'Step 3/3: Summarizing data...'

      this.clips.sort((a, b) => {
        const getLikeCount = (clip) => {
          switch (clip.type) {
            case 'twitter':
              return clip.user.public_metrics.like_count || 0
            case 'bluesky':
              return clip.stats.likes || 0
            case 'youtube':
              return parseInt(clip.stats.likeCount, 10) || 0
            default:
              return 0
          }
        }

        const likesA = getLikeCount(a)
        const likesB = getLikeCount(b)

        return likesB - likesA
      })

      this.totalVisits = this.calculateTotalVisits()
      this.starredArticles = this.clips.slice(0, 3)
      console.log('CLIPS ARE RIGHT HERE ---  > ', this.clips)
      this.clipChartData = this.processClips(this.clips)
      this.socialTotals = this.getSocialTotals()

      this.loading = false
      this.creating = false
      this.threadModalOpen = false
    },

    async getTrafficData() {
      this.loadingText = 'Step 2/4: Gathering traffic...'
      try {
        const res = await Comms.api.getTrafficData({
          urls: this.urls,
        })
        this.traffic = res
        this.getSocialData()
      } catch (e) {
        console.error(e)
        this.loading = false
        this.urlsSet = false
        this.$toast('Error uploading clips, try again', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async getSocialData() {
      this.loadingText = 'Step 3/4: Summarizing data...'
      try {
        const res = await Comms.api.getSocialData({
          urls: this.urls,
        })
        this.socialData = res

        this.combineArticlesWithTraffic()
      } catch (e) {
        console.error(e)
        this.loading = false
        this.urlsSet = false
        this.$toast('Error uploading clips, try again', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async getReportSummary() {
      this.loadingText = 'Step 4/4: Generating report...'
      let clips = this.prepareClips(this.clips)
      this.preppedClips = clips

      try {
        const res = await Comms.api.getReportSummary({
          clips: clips,
          brand: this.brand,
          social: false,
        })
        this.summary = res.summary
          .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
          .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')
          .replace(/^### (.*$)/gim, '<h3>$1</h3>')
          // Convert #### to <h4></h4>
          .replace(/^#### (.*$)/gim, '<h4>$1</h4>')
          // Convert ## to <h2></h2> (if needed)
          .replace(/^## (.*$)/gim, '<h2>$1</h2>')
          // Convert # to <h1></h1> (if needed)
          .replace(/^# (.*$)/gim, '<h1>$1</h1>')

        this.loading = false
        this.creating = false
        this.threadModalOpen = false
      } catch (e) {
        console.error(e)

        this.urlsSet = false
        this.loading = false
        this.$toast('Error uploading clips, try again', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    prepareClips(clips) {
      return clips.map(
        (a) =>
          `Description:${a.description ? a.description : ''} Date:${a.date}, Source:${
            a.source
          }, Author/s :${a.author ? a.author[0] : 'Unknown'}, Unique visitors: ${
            a.traffic ? a.traffic.users : 0
          },  Social Media engagement / shares: ${
            this.socialData[a.url] && this.socialData[a.url][0]
              ? `Facebook: ${this.socialData[a.url][0]['total_facebook_shares']}, Reddit: ${
                  this.socialData[a.url][0]['total_reddit_engagements']
                }, Pinterest: ${this.socialData[a.url][0]['pinterest_shares']}, X/Twitter: ${
                  this.socialData[a.url][0]['twitter_shares']
                } `
              : 'none'
          } `,
      )
    },
    combineArticlesWithTraffic() {
      this.clips = this.clips.map((article) => {
        const domain = article.source.replace(/^https?:\/\//, '').replace(/^www\./, '')
        const traffic = this.traffic[domain] || null
        return {
          ...article,
          traffic,
        }
      })

      this.clips = this.clips.sort((a, b) => {
        const trafficA = a.traffic ? a.traffic.users : 0 // if no traffic, set to 0
        const trafficB = b.traffic ? b.traffic.users : 0 // if no traffic, set to 0
        return trafficB - trafficA // sort in descending order
      })

      this.totalVisits = this.calculateTotalVisits()
      this.socialTotals = this.getSocialTotals()
      this.clipChartData = this.processClips(this.clips)
      this.getReportSummary()
    },
    processClips(clips) {
      const dateMap = new Map()

      if (this.selectedSearch.meta_data.type === 'news') {
        clips.forEach((clip) => {
          const date = clip.date ? new Date(clip.date).toLocaleDateString() : null
          if (date && clip.traffic && clip.traffic.users) {
            if (dateMap.has(date)) {
              const existingData = dateMap.get(date)
              dateMap.set(date, {
                clipCount: existingData.clipCount + 1,
                totalUsers: existingData.totalUsers + Number(clip.traffic.users),
              })
            } else {
              dateMap.set(date, {
                clipCount: 1,
                totalUsers: Number(clip.traffic.users),
              })
            }
          }
        })
      } else {
        clips.forEach((clip) => {
          const date = clip.created_at ? new Date(clip.created_at).toLocaleDateString() : null
          if (date) {
            if (dateMap.has(date)) {
              const existingData = dateMap.get(date)
              let userCount

              switch (clip.type) {
                case 'twitter':
                  userCount = clip.user.public_metrics.followers_count || 0
                  break
                case 'bluesky':
                  userCount =
                    clip.stats.likes +=
                    clip.stats.replies +=
                    clip.stats.reposts +=
                      clip.stats.quotes || 0
                  break
                case 'youtube':
                  userCount = parseInt(clip.stats.viewCount, 10) || 0
                  break
                default:
                  userCount = 0
                  break
              }

              dateMap.set(date, {
                clipCount: existingData.clipCount + 1,
                totalUsers: existingData.totalUsers + Number(userCount),
              })
            } else {
              let userCount

              switch (clip.type) {
                case 'twitter':
                  userCount = clip.user.public_metrics.followers_count || 0
                  break
                case 'bluesky':
                  userCount =
                    clip.stats.likes +=
                    clip.stats.replies +=
                    clip.stats.reposts +=
                      clip.stats.quotes || 0
                  break
                case 'youtube':
                  userCount = parseInt(clip.stats.viewCount, 10) || 0
                  break
                default:
                  userCount = 0
                  break
              }

              dateMap.set(date, {
                clipCount: 1,
                totalUsers: Number(userCount),
              })
            }
          }
        })
      }

      const sortedDates = Array.from(dateMap.keys()).sort((a, b) => {
        return new Date(a) - new Date(b)
      })

      const dateList = []
      const clipCountList = []
      const usersList = []

      sortedDates.forEach((date) => {
        const data = dateMap.get(date)
        dateList.push(date)
        clipCountList.push(data.clipCount)
        usersList.push(data.totalUsers)
      })

      return {
        dateList,
        clipCountList,
        usersList,
      }
    },
    calculateTotalVisits() {
      let totalVisits = 0

      if (this.selectedSearch.meta_data.type === 'news') {
        for (let key in this.traffic) {
          if (this.traffic[key].users) {
            totalVisits += parseInt(this.traffic[key].users, 10)
          }
        }
      } else {
        for (let i = 0; i < this.clips.length; i++) {
          let clip = this.clips[i] // Get the clip from the array
          let userCount = 0 // Initialize userCount for each clip

          switch (clip.type) {
            case 'twitter':
              userCount = clip.user.public_metrics.followers_count || 0
              break
            case 'bluesky':
              userCount =
                (clip.stats.likes || 0) +
                (clip.stats.replies || 0) +
                (clip.stats.reposts || 0) +
                (clip.stats.quotes || 0)
              break
            case 'youtube':
              userCount = parseInt(clip.stats.viewCount, 10) || 0
              break
            default:
              userCount = 0
              break
          }

          // Add userCount to totalVisits
          totalVisits += userCount
        }
      }

      return totalVisits
    },

    // getSocialTotals() {
    //   let totalFacebookLikes = 0
    //   let totalRedditLikes = 0
    //   let totalPinterestLikes = 0
    //   let totalTwitterLikes = 0

    //   for (const url in this.socialData) {
    //     if (this.socialData.hasOwnProperty(url)) {
    //       const data = this.socialData[url]

    //       if (data[0] && data[0].total_facebook_shares) {
    //         totalFacebookLikes += data[0].total_facebook_shares
    //       }

    //       if (data[0] && data[0].total_reddit_engagements) {
    //         totalRedditLikes += data[0].total_reddit_engagements
    //       }

    //       if (data[0] && data[0].twitter_shares) {
    //         totalTwitterLikes += data[0].twitter_shares
    //       }

    //       if (data[0] && data[0].pinterest_shares) {
    //         totalPinterestLikes += data[0].pinterest_shares
    //       }
    //     }
    //   }

    //   return {
    //     totalFacebookLikes,
    //     totalRedditLikes,
    //     totalPinterestLikes,
    //     totalTwitterLikes,
    //   }
    // },
    getSocialTotals() {
      let totalFacebookLikes = 0
      let totalRedditLikes = 0
      let totalPinterestLikes = 0
      let totalTwitterLikes = 0
      let totalBlueskyLikes = 0
      let totalYoutubeLikes = 0

      if (this.selectedSearch.meta_data.type === 'news') {
        const articlesWithSocialTotals = this.clips.map((article) => {
          const socialData = this.socialData[article.url] || null
          let totalShares = 0

          if (socialData && socialData[0]) {
            const {
              total_facebook_shares,
              total_reddit_engagements,
              twitter_shares,
              pinterest_shares,
            } = socialData[0]
            totalShares += total_facebook_shares || 0
            totalShares += total_reddit_engagements || 0
            totalShares += twitter_shares || 0
            totalShares += pinterest_shares || 0

            totalFacebookLikes += total_facebook_shares || 0
            totalRedditLikes += total_reddit_engagements || 0
            totalTwitterLikes += twitter_shares || 0
            totalPinterestLikes += pinterest_shares || 0
          }

          return {
            ...article,
            totalShares,
          }
        })

        this.starredArticles = articlesWithSocialTotals
          .sort((a, b) => b.totalShares - a.totalShares)
          .slice(0, 3)

        return {
          totalFacebookLikes,
          totalRedditLikes,
          totalPinterestLikes,
          totalTwitterLikes,
        }
      } else {
        for (let i = 0; i < this.clips.length; i++) {
          let clip = this.clips[i]
          let twitterLikes = 0
          let blueLikes = 0
          let ytLikes = 0

          switch (clip.type) {
            case 'twitter':
              twitterLikes = clip.user.public_metrics.like_count || 0
              break
            case 'bluesky':
              blueLikes = clip.stats.likes || 0
              // (clip.stats.replies || 0) +
              // (clip.stats.reposts || 0) +
              // (clip.stats.quotes || 0)
              break
            case 'youtube':
              ytLikes = parseInt(clip.stats.likeCount, 10) || 0
              break
          }

          totalTwitterLikes += twitterLikes
          totalYoutubeLikes += ytLikes
          totalBlueskyLikes += blueLikes
        }

        return {
          totalTwitterLikes,
          totalYoutubeLikes,
          totalBlueskyLikes,
        }
      }
    },

    async runReport() {
      this.loading = true
      try {
        const res = await Comms.api.runReport({
          urls: this.urls,
          name: this.brand,
        })

        this.loading = false
      } catch (e) {
        console.error(e)
        this.loading = false
      } finally {
      }
    },
    handleInput() {
      const result = this.processUrls(this.reportUrls)
      this.urls = result.urls
      this.urlCount = result.count
    },
    processUrls(inputText) {
      const lines = inputText
        .split(/[\n,]+/)
        .map((line) => line.trim())
        .filter((line) => line !== '')
      const urls = []
      let count = 0

      const validTLDs = new Set([
        'com',
        'org',
        'net',
        'int',
        'edu',
        'gov',
        'mil',
        'co',
        'io',
        'me',
        'biz',
        'info',
        'xyz',
        'online',
        'site',
        'club',
        'shop',
        'blog',
        'web',
        'art',
        'app',
        'dev',
        'tech',
        'store',
        'ai',
        'us',
        'uk',
      ])

      function levenshteinDistance(a, b) {
        const matrix = []
        let i
        for (i = 0; i <= b.length; i++) {
          matrix[i] = [i]
        }
        let j
        for (j = 0; j <= a.length; j++) {
          matrix[0][j] = j
        }
        for (i = 1; i <= b.length; i++) {
          for (j = 1; j <= a.length; j++) {
            if (b.charAt(i - 1) === a.charAt(j - 1)) {
              matrix[i][j] = matrix[i - 1][j - 1]
            } else {
              matrix[i][j] = Math.min(
                matrix[i - 1][j - 1] + 1,
                matrix[i][j - 1] + 1,
                matrix[i - 1][j] + 1,
              )
            }
          }
        }
        return matrix[b.length][a.length]
      }

      function findClosestTLD(tld) {
        let minDistance = Infinity
        let closestTLD = null
        for (let validTLD of validTLDs) {
          const distance = levenshteinDistance(tld, validTLD)
          if (distance < minDistance) {
            minDistance = distance
            closestTLD = validTLD
          }
        }
        return minDistance === 1 ? closestTLD : null
      }

      for (let line of lines) {
        line = line.trim()
        if (line === '') continue

        const tldMatch = line.match(/\.([a-zA-Z]{2,})$/)
        if (tldMatch) {
          const tld = tldMatch[1].toLowerCase()
          if (!validTLDs.has(tld)) {
            const correctedTLD = findClosestTLD(tld)
            if (correctedTLD) {
              line = line.slice(0, -tld.length) + correctedTLD
            }
          }
        }
        urls.push(line)
        count++
      }

      return { urls, count }
    },

    changeView(txt) {
      this.view = txt
      if (txt === 'starred') {
        this.scrollToTopDivider()
      }
    },
    setUrls() {
      this.urlsSet = true
      this.scrollToChatTop()
    },
    uploadImage(event) {
      const file = event.target.files[0]
      this.mainImage = file

      // Check if a file was selected
      if (!file) {
        this.fileName = ''
        alert('No file selected.')
        return
      }

      // Check for allowed file types
      if (!this.allowedFormats.includes(file.type)) {
        alert('Only JPEG, PNG, and SVG files are allowed.')
        this.fileName = ''
        return
      }

      // Check for file size
      if (file.size > this.maxSize) {
        alert('File size should not exceed 2MB.')
        this.fileName = ''
        return
      }

      const reader = new FileReader()

      // Logic for JPEG files: perform extra binary validation
      if (file.type === 'image/jpeg') {
        reader.onload = (e) => {
          const arrayBuffer = e.target.result
          const uint8Array = new Uint8Array(arrayBuffer)

          // Check JPEG Start and End markers
          const isValidJPEG =
            uint8Array[0] === 0xff &&
            uint8Array[1] === 0xd8 &&
            uint8Array[uint8Array.length - 2] === 0xff &&
            uint8Array[uint8Array.length - 1] === 0xd9

          if (!isValidJPEG) {
            alert('The file is not a valid JPEG image.')
            this.fileName = ''
            this.loading = false
            return
          }

          // If valid, read again as DataURL for preview
          this.fileName = file.name
          this.scrollToChatTop()
          const dataUrlReader = new FileReader()
          dataUrlReader.onload = (e) => {
            this.uploadedImageUrl = e.target.result
            this.loading = false
          }
          dataUrlReader.readAsDataURL(file)
        }

        reader.onerror = () => {
          alert('Error reading file.')
          this.fileName = ''
          this.loading = false
        }

        // Read the file as an ArrayBuffer to access binary data for validation
        reader.readAsArrayBuffer(file)
      } else {
        this.fileName = file.name
        this.scrollToChatTop()
        // For non-JPEG files, keep the original logic
        reader.onload = (e) => {
          const imageDataUrl = e.target.result
          this.uploadedImageUrl = imageDataUrl
          this.loading = false
        }

        reader.onerror = () => {
          alert('Error reading file.')
          this.fileName = ''
          this.loading = false
        }

        reader.readAsDataURL(file)
      }
    },
    // uploadImage(event) {
    //   const file = event.target.files[0]
    //   this.mainImage = file

    //   if (!file) {
    //     this.fileName = ''
    //     alert('No file selected.')
    //     return
    //   }

    //   if (!this.allowedFormats.includes(file.type)) {
    //     alert('Only JPEG, PNG, and SVG files are allowed.')
    //     this.fileName = ''
    //     return
    //   }

    //   if (file.size > this.maxSize) {
    //     alert('File size should not exceed 2MB.')
    //     this.fileName = ''
    //     return
    //   }

    //   this.loading = true
    //   this.fileName = file.name
    //   this.scrollToChatTop()

    //   const reader = new FileReader()

    //   reader.onload = (e) => {
    //     const imageDataUrl = e.target.result
    //     this.uploadedImageUrl = imageDataUrl
    //     this.loading = false
    //   }

    //   reader.onerror = () => {
    //     alert('Error reading file.')
    //     this.fileName = ''
    //     this.loading = false
    //   }

    //   reader.readAsDataURL(file)
    // },
    generateReportSearch() {
      if (!this.reportName) {
        this.reportName = this.searchText
        this.searchText = ''
        this.$refs.textarea.dispatchEvent(new Event('textarea-clear'))
        this.scrollToChatTop()
        return
      } else if (!this.brand) {
        this.brand = this.searchText
        this.searchText = ''
        this.$refs.textarea.dispatchEvent(new Event('textarea-clear'))
        this.scrollToChatTop()
        return
      }
    },
    scrollToChatTop() {
      this.$nextTick(() => {
        const chatWindow = this.$refs.chatWindow
        chatWindow.scrollTop = chatWindow.scrollHeight
      })
    },
  },
  directives: {
    autoresize: {
      inserted(el) {
        function adjustTextareaHeight() {
          el.style.height = 'auto'
          el.style.height = el.scrollHeight + 'px'
        }

        el.addEventListener('input', adjustTextareaHeight)
        el.addEventListener('focus', adjustTextareaHeight)
        el.addEventListener('textarea-clear', function () {
          el.value = ''
          el.style.height = 'auto'
        })

        adjustTextareaHeight()
      },
    },

    typed: {
      bind(el, binding) {
        let text = binding.value
        let index = 0
        el.innerHTML = ''

        function type() {
          if (index < text.length) {
            el.innerHTML += text.charAt(index)
            index++
            setTimeout(type, 12)
          }
        }

        type()
      },
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.rotate-img {
  transform: rotate(180deg);
}

.container-left-below {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 5px;
  position: absolute;
  left: 0;
  bottom: 44px;
  min-height: 150px;
  max-height: 250px;
  overflow-y: scroll;
  width: 350px;
  padding: 0 0 16px 0;
  background-color: white;
  box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);
  z-index: 9;

  p {
    font-family: $thin-font-family;
    margin: 0;
    padding: 8px 16px;
    width: 100%;
    font-size: 14px;
    &:hover {
      background-color: $soft-gray;
      cursor: pointer;
    }
  }

  section {
    position: sticky;
    top: 0;
    margin: 0;
    background-color: white;
    font-family: $base-font-family;
    font-weight: 100;
    padding: 16px;
    width: 100%;
    z-index: 3;

    h3 {
      margin: 0;
    }
  }
}

.relative {
  position: relative;
}

.drop-header-alt {
  padding: 8px 10px;
  width: fit-content;
  background-color: white;
  font-size: 14px !important;
  border-radius: 16px;
  display: flex;
  flex-direction: row;
  align-items: center;
  cursor: pointer;
  margin: 8px 0;
  font-family: $thin-font-family;

  @media only screen and (max-width: 600px) {
    font-size: 12px !important;
  }

  img {
    margin: 0 8px;
    filter: invert(40%);

    @media only screen and (max-width: 600px) {
      // display: none;
    }
  }

  small {
    font-size: 14px;
    margin-left: 4px !important;
    font-family: $base-font-family;
    max-width: 55px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }

  p,
  small {
    margin: 0;
    padding: 0;
  }

  &:hover {
    background-color: $soft-gray;
  }
}

.turq-bg {
  background-color: $lite-blue !important;
}

.lite-bg {
  background-color: $lite-blue !important;
  img {
    filter: invert(100%) !important;
  }
}

.img-container-stay-alt {
  padding: 3px 5px 3px 7px;
  border-radius: 50%;
  background-color: $soft-gray;

  img {
    margin: 0;
    padding: 0;
  }
}

.opaque {
  opacity: 0.3 !important;
  cursor: text;
}

.floating-panel {
  position: absolute;
  right: 15vw;
  bottom: 10vh;
  box-shadow: 1px 3px 6px rgba(0, 0, 0, 0.2);
  border-radius: 100%;
  padding: 8px 10px;
  background: transparent;
  z-index: 100;
  cursor: pointer;
}

.expanded {
  border-radius: 20px !important;

  img {
    margin: 10px 0;
  }
}

.panel-options {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  img {
    filter: invert(40%);
  }
}

.s-tooltip-right {
  visibility: hidden;
  width: 120px;
  background-color: $graper;
  color: white;
  text-align: center;
  border-radius: 4px;
  padding: 6px 2px;
  position: absolute;
  z-index: 100;
  top: 100%;
  left: 115%;
  margin-top: -30px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  font-size: 13px;
  line-height: 1.4;
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
}

.s-tooltip-left {
  visibility: hidden;
  width: 120px;
  background-color: $graper;
  color: white;
  text-align: center;
  border-radius: 4px;
  padding: 6px 2px;
  position: absolute;
  z-index: 100;
  top: 100%;
  right: 120%;
  margin-top: -36px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  font-size: 13px;
  line-height: 1.4;
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
}

.s-wrapper {
  position: relative;
  display: inline-block;
}

.s-wrapper:hover .s-tooltip-left,
.s-wrapper:hover .s-tooltip-right {
  visibility: visible;
  opacity: 1;
}

a {
  text-decoration: none;
  color: $dark-black-blue;
}

.img-container-stay-small-txt {
  cursor: pointer;
  font-family: $base-font-family;
  color: $dark-black-blue;
  padding: 4px 8px !important;
  border-radius: 9px;
  background-color: $silver;
  display: flex;
  flex-direction: row;
  align-items: center;
  font-size: 14px;

  img {
    filter: invert(20%);
    margin: 0 0 0 8px;
    padding: 0;
  }
}

.input-container-small {
  border: 1px solid rgba(0, 0, 0, 0.185);
  transition: box-shadow 0.3s ease;
  padding: 2px 0;
  border-radius: 9px;
  width: 100%;
  color: $base-gray;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  flex-direction: row;
  background-color: white;
  margin-top: 16px;

  img {
    filter: invert(40%);
  }

  input {
    background: transparent;
    padding-left: 16px !important;
    font-family: $thin-font-family;
    width: 100%;
  }
}

.abs-img-left {
  position: absolute;
  top: 30%;
  left: -32px;
}

.abs-top-right {
  position: absolute;
  top: 12px;
  right: 12px;
}

.abs-top {
  position: absolute;
  bottom: 110%;
  right: 0;
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 10px 16px;
  width: 400px;
  background-color: white;
  border-radius: 6px;
  box-shadow: 1px 3px 6px rgba(0, 0, 0, 0.2);
  cursor: text;
}

.elipsis-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;
}

.gold-filter {
  filter: invert(74%) sepia(68%) saturate(1511%) hue-rotate(358deg) brightness(95%) contrast(106%);
}

.blue-filter {
  filter: invert(50%) sepia(6%) saturate(4941%) hue-rotate(159deg) brightness(100%) contrast(87%);
}

.fadein {
  transition: opacity 1s ease-out;
  opacity: 0;
  animation: fadeIn 1s forwards;
}

@keyframes fadeIn {
  to {
    opacity: 1;
  }
}

.bottom-border {
  border-bottom: 2px solid rgba(0, 0, 0, 0.05);
  padding-bottom: 12px;
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

.report-body {
  font-family: $thin-font-family;
  line-height: 1.5;
  font-size: 14px;
}

.no-letter-margin {
  p {
    margin: 0 !important;
  }
}

.img-mar {
  img {
    margin-right: 4px;
  }
}

.small-text {
  font-size: 13px;
}

.medium-txt {
  font-size: 18px;
}

.bottom-margin {
  margin-bottom: 24px;
}

.bottom-margin-m {
  margin-bottom: 12px;
}

.container {
  background-color: white;
  padding: 16px;
  border-radius: 9px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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

.col {
  display: flex;
  flex-direction: column;
}

.active {
  background-color: $soft-gray;
}

.pre-text {
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 16px;
  line-height: 32px;
  word-wrap: break-word;
  white-space: pre-wrap;
  outline: none;
}

.pre-text:focus {
  outline: 2px solid $lite-blue;
}

::v-deep ::selection {
  background-color: $lite-blue !important;
  color: white;
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

.photo-header-alt {
  height: 150px;
  width: 150px;
  margin: 0;
  object-fit: cover;
  object-position: top;
  border-radius: 5px;
}

.space-between-bottom {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: flex-end;
  width: 100%;
}

.photo-header {
  // height: 250px;
  // width: 100%;
  // margin: 0;
  // object-fit: cover;
  // object-position: top;
  // border-radius: 5px;

  width: 100%;
  aspect-ratio: 16/9;
  margin: 0;
  object-fit: cover;
  border-radius: 5px;
}

.photo-header-small {
  max-height: 500px;
  width: 100%;
  aspect-ratio: 16/9;
  margin: 0;
  object-fit: cover;
  border-radius: 5px;
}

.left-nav {
  width: 60px;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  background-color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  // box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);

  .nav-links {
    list-style: none;
    padding: 0;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    .nav-item {
      margin: 10px 0;
      display: flex;
      justify-content: center;
      cursor: pointer;

      div {
        padding: 9px;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        transition: background 0.3s ease;
        &:hover {
          background-color: $soft-gray;
        }

        img {
          margin: 0;
        }
      }
    }
  }
}

.thin-font {
  font-family: $thin-font-family !important;
}

.bold-font {
  font-family: $base-font-family !important;
}

.primary-button {
  @include dark-blue-button();
  padding: 8px 12px;
  border: none;
  border-radius: 16px;
  img {
    filter: invert(100%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin-right: 8px;
  }
}

.flex-end {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
}

@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(359deg);
  }
}

.rotation {
  animation: rotation 2s infinite linear;
}

.file-input-wrapper {
  display: flex;
  flex-direction: row;
  align-items: center;
  font-family: $thin-font-family;
}

.file-input-label {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
}

.file-input {
  display: none;
}

.large-input-container {
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.025);
  border-radius: 28px;
  background-color: white;
  width: 100%;
  margin-bottom: 8px;

  @media only screen and (max-width: 600px) {
    width: 94vw !important;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
    width: 70vw !important;
  }
}

.input-container-gray {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s ease;
  padding: 18px 0 14px 0;
  border-radius: 24px;
  width: 100%;
  color: $base-gray;
  position: relative;
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  flex-direction: column;
  background-color: white;

  section {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    flex-direction: row;
  }

  img {
    filter: invert(40%);
  }
}

.area-input {
  width: 100%;
  margin-bottom: 0.25rem;
  max-height: 120px !important;
  padding: 0 1.25rem;
  line-height: 1.5;
  outline: none;
  border: none;
  letter-spacing: 0.5px;
  font-size: 14px;
  font-family: $thin-font-family !important;
  font-weight: 400;
  border: none !important;
  resize: none;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
  color: $dark-black-blue;
  background-color: transparent;
}
.area-input::-webkit-scrollbar {
  width: 4px;
  height: 0px;
}
.area-input::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.area-input::-webkit-scrollbar-track {
  margin-top: 24px;
}

.text-area-input {
  padding-top: 1rem;
}

input,
textarea {
  font-family: $thin-font-family;
}

input::placeholder {
  font-family: $thin-font-family;
}
input:disabled {
  cursor: not-allowed;
}
textarea:disabled {
  cursor: not-allowed;
}
textarea::placeholder {
  font-family: $thin-font-family;
}

.big-chat-bubble {
  width: fit-content;
  border-radius: 12px;
  padding: 8px 16px;
  margin: 12px 0;
  background-color: white;
  box-shadow: 1px 2px 6px rgba(0, 0, 0, 0.05);
}

.space-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.row-even {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  width: 50%;
}

.row {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.rows {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 4px 0;

  div {
    width: 40%;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: flex-end;
    // padding-left: 12px;

    img {
      margin-right: 8px;
    }
  }
}

.reports {
  height: 100vh;
  width: 100vw;
  padding: 32px 18vw;
}
.chat-window {
  height: 96vh;
  display: flex;
  align-items: center;
  flex-direction: column;
  justify-content: space-evenly;
  padding: 0 5vw;

  &__header {
    width: 100%;
    position: sticky;
    top: 0;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    padding: 48px 0 12px 0;
    p {
      font-family: $base-font-family;
      font-size: 18px !important;
    }
  }

  &__body {
    height: 100%;
    width: 100%;
    overflow-y: scroll;
    padding: 0 4px;
  }

  &__footer {
    position: sticky;
    bottom: 0;
    width: 100%;
    padding: 24px 0;
    display: flex;
    align-items: center;
    justify-content: center;
    // border-top: 1px solid rgba(0, 0, 0, 0.1);
  }

  &__chat-bubble {
    line-height: 1.5;
    width: fit-content;
    border-radius: 20px;
    padding: 8px 16px;
    margin: 12px 0;
    background-color: white;
    box-shadow: 1px 2px 6px rgba(0, 0, 0, 0.05);

    img {
      margin-right: 6px;
    }

    p {
      margin: 0;
    }
  }
}

.cursor {
  cursor: pointer;
}
.text {
  cursor: text;
  outline: 2px solid $lite-blue;
}

.bio-modal {
  margin-top: 72px;
  @media only screen and (max-width: 600px) {
    margin-top: 62px;
  }

  width: 70vw;
}

.med-modal {
  width: 55vw !important;
}
.med-container {
  width: 48vw !important;
  padding: 0 16px 0 16px !important;
}
.bio-container {
  width: 60vw;
  max-height: 75vh;
  position: relative;
  overflow-y: scroll;
  color: $base-gray;
  font-family: $thin-font-family;
  padding: 0 24px 0 24px;

  label {
    font-size: 14px;
  }
  @media only screen and (max-width: 600px) {
    width: 95%;
    padding: 0;
  }

  header {
    // border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    background-color: white;
    padding: 0 0 8px 0;

    p {
      font-weight: bold;
    }
  }

  footer {
    // border-top: 1px solid rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: flex-end;
    position: sticky;
    bottom: -1px;
    background-color: white;
    margin: 0;
    padding: 24px 0 0 0;

    .row {
      margin-bottom: 8px;

      .secondary-button {
        margin: 0;
      }
    }
  }

  section {
    padding: 24px 0 16px 0;
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    overflow: scroll;

    .bio-body {
      word-wrap: break-word;
      white-space: pre-wrap;
      font-size: 15px;
      overflow: scroll;
    }

    aside {
      display: flex;
      flex-direction: column;
      margin-left: 40px;

      img {
        height: 110px;
        width: 120px;
        margin-bottom: 16px;
        object-fit: cover;
        cursor: text;
        border-radius: 4px;
        border: 1px solid rgba(0, 0, 0, 0.1);
      }
    }
  }
}

.bold {
  font-family: $base-font-family;
}

.header-alt {
  h2 {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    background-color: white;
    font-family: $base-font-family;
  }
  position: sticky;
  top: 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0 0 8px 0;
}
</style>
