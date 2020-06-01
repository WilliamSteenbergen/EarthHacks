### Inspiration

Living in California, our team was keenly aware of how the past few years of wildfires have affected our lives: increasing air pollution, participating in planned public safety power shut-offs, and supporting friends through tragic losses. As we dove into our research, it became clear that the community-level devastation affected communities of all sizes, with an outsized impact on those who are most vulnerable due to their age, education, language ability, mobility, and socio-economic status. As we thought about where we could add value, we wanted to ensure we were prioritizing those who needed the most help. 

Our original vision was to build a defensible-space tool for homeowners to better understand, manage, and implement the jurisdiction's requirements. Interviews in the fire community revealed that over 70% of homes pass on their first inspection, while the remaining 30% often require multiple inspections. The current inspection process is highly manual and inefficient for Cal-Fire; oftentimes inspectors don't return to re-inspect a home due to the progression of the fire season and competing priorities.

This led us to turn our efforts to Cal-Fire, which hires 130 inspectors each year to monitor compliance across their 31M acres of State Responsibility Area (SRA). As we spoke with Cal-Fire, we started to hear pain points around information accessibility and defensible space during live fire events.  

**We decided to investigate the power of remote sensing to detect defensible space during live fire events, optimistic that the combination of this information with social vulnerability data would help to ensure faster, more efficient, and more equitable live fire response.**

### Our Tool

Our tool assesses predicted fire damage at a "neighborhood" level for groups of California homes in SRA jurisdiction, integrating community vulnerability data, to help Cal-Fire inform live fire response.  The tool may also help to triage proactive defensible space inspection to the most risk-prone homes when no fire is present. 

It does this by:
1) Improving CALFIRE's information access during live fire events by providing granular information on neighborhood / home defensible space, damage risk, and community vulnerability.
2) Enabling prioritization of the most-at-risk neighborhoods/homes by indexing relative risk either during a live fire event or proactively when CALFIRE is carrying out its inspection process.

Click around in our wireframe prototype here:
Use Case 1 | [Live Fire Event] (https://www.figma.com/proto/6ggVeNU7ffl2uPSvmHqcWj/Firesafe?node-id=14%3A1&scaling=scale-down)
Use Case 2 | [Inspection Triaging] (https://www.figma.com/proto/6ggVeNU7ffl2uPSvmHqcWj/Firesafe?node-id=25%3A41&scaling=contain)
###How we built it

Our system primarily depends on predicting the relative "burn risk" among "threatened communities" (defined as a .5 x .5 KM area).  This risk, as well as information informing that prediction and social vulnerability information relevant to that community is then visualized to response planners.

In either a live fire or proactive planning event, the tool takes as use input a lat/long that defines an active or theoretical fire boundary.  The system then simulates a series of potential boundaries for the fire and uses the minimum bounding geometry of those various simulations to define the population of "threatened communities".  Today, our simulation engine is quite naive as extensive work by groups such as FlamMap and Crowley et al. has been carried out in this domain and we simply did not have the scope to integrate these models into our prototype as we would in a production system.  

With the population of "threatened communities" defined as the overlap of the potential burn radius and populated areas ("the WUI"), a series of individual "neighborhoods" is defined via a simple .5x.5KM grid over-layed on this intersection.  For each section of this grid, the most recent Landsat 30M resolution image (R, G, B, and Infrared Bands) is extracted from Google Earth engine and passed into the core prediction model.  It's worth noting that the use of higher resolution imagery such as Planet Labs 3M resolution or even Sentinel 10M resolution could be used as available.  

The core prediction model is a convolutional neural net with Z layers that takes as input a 4 channel, 152x152 pixel image, and returns a single percentage value (0-100%), which represents the percentage of the image that is likely to truly be damaged or scorched should a fire "come through" the entirety of that area.  The model was trained over M training examples for H epochs.  The ground truth for this training set was established using an unsupervised clustering and pixel difference algorithm adapted from Rossi et al. that approximated the damaged or scorched areas in populated regions in past fire events.  Because the ground truth of this model was difficult to verify, we do not feel comfortable reporting the accuracy of this model, however we are reasonably confident that given a more robust labeling based approach or better verification of the unsupervised method, such a model could likely achieve high performance in production.  

In order to enable users to interpret the core prediction model, we also layered in the popular Shap Deep Explainer algorithm from Lundeberg et al.  So-called "Shapley Values" allow each pixel's "contribution" to a prediction to be scored in terms of both direction and magnitude.  As a result, it is possible that this interpretability method could, for an at-risk area, call planners' attention to a particularly risk-prone home or other sub-region of that area.  These areas may or may not correlate to areas with poor defensible space, but we do believe a label-based, defensible space classifier could serve as an important additional input to this piece of the pipeline.  

Lastly with a series of "neighborhoods" or "threatened communities" defined, a burn risk prediction (simulator), a damage risk prediction (CNN prediction model), and a social vulnerability index score (CDC's SVI) established, we visualize these metrics for a given event to the end user. 

On the whole, we believe this group of technologies, especially when put into a more robust production implementation, can ensure faster, more efficient, and more equitable live fire response and proactive management.

### Challenges

With no prior geo-spatial backgrounds, our team faced several challenges in building and manipulating our data pipeline. Specific data challenges included:
- Data type mismatches due to 'snapped pixels' forcing "squeezed" dimensions
- Only low resolution imagery available
- Difficulty implementing efficient cloud-cover removal and composite scoring
- Lack of familiarity with correct thresholds for filtering, scoring, etc. 

These data challenges were also coupled with simple time constraints such as: 
- Not enough time to collect sufficient labeled images, forcing use of unsupervised approach
- Forced to put the "hack" in "hackathon" at a number of points in the pipeline
- Difficulty building out a robust UI despite complete model implementations

Lastly, the nature of these constraints did limit us algorithmically:
- CNN predictions focused on entire image and not "window panes" or sub-images
- Simulation step was Naive and did not leverage RL or other known simulation techniques


### Accomplishments that we're proud of

We're proud of both the process and the output. Along the way, our team hit many roadblocks. Despite our varying levels of technical expertise and comfort with geospatial data, we were able to find ways for everyone to push the project forward each week whether it was through primary research, secondary analysis, soliciting help, or hacking away. 

While our team would have liked to produce more, we are proud that our vision of creating a live response and defensible space management tool contributes meaningfully to the existing options currently available to Cal-Fire and solves an important pain point. In particular, we view the inclusion of community vulnerability into this project as an imperative for any "go forward" related projects.


### What we learned

We learned an immense amount about fire-risk in California and the monumental challenges ahead as global warming continues to heighten wildfire risks. Within the realm of defensible space, we learned this is a highly complex and fragmented area with regulations at both the state and country level. We heard a lot of stories about when the law and reality took divergent paths, fueled by competing end goals that ranged from compliance to education. One of the largest barriers in this space is simply combating human behavior: compelling individuals to act for the good of their neighborhoods, despite their own personal landscaping desires. 

Technically, we learned the maintaining data integrity while manipulating geo-spatial data is incredibly challenging. Due to the myriad different data types across different layers, we struggled to extract the data we wanted and at times had to "hack" our way to success.  Despite backgrounds in a variety of machine learning techniques, including deep learning, this was also the first time many of us did in-depth work with multi-channel image data and convolutional neural nets.  

Finally, we left his hackathon with the conclusion that while much progress has been made in certain areas of machine learned statistical modeling across the domain of wildland fires, there is considerable room for systems based thinking to provide more holistic solutions.  

### What's next for Fire Risk Tracking for Vulnerable Communities

We are excited to apply the knowledge we have learned in our respective fields both in an academic and professional capacity. This has been an incredible learning experience for us all, and all four of us are grateful for a great quarter! 

